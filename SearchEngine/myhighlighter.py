
from whoosh.highlight import Highlighter, Token, groupby, set_matched_filter, top_fragments

class SeparatTextHighlighter(Highlighter):
    """ A class which saves the data for creating highlights later with the text
    
    Attributes:
        pinpoint_bool (bool): whether pinpoint highlighting is possible
        words (frozenset)
        tokens (list)
        analyzer (whoosh.analysis.Analyzer)
    """

    def __init__(self, hitobj, fieldname):
        """
        Prepare everything for creating highlights without knowing the hitobj anymore

        Args:
            hitobj (whoosh.searching.Hit): The hit object for which the highlights are
            fieldname (str): The name of the field in which to search
        """
        super().__init__()
        results = hitobj.results
        schema = results.searcher.schema
        field = schema[fieldname]
        to_bytes = field.to_bytes
        from_bytes = field.from_bytes

        if results.has_matched_terms():
            bterms = (term for term in results.matched_terms()
                      if term[0] == fieldname)
        else:
            bterms = results.query_terms(expand=True, fieldname=fieldname)
        # Convert bytes to unicode
        self.words = frozenset(from_bytes(term[1]) for term in bterms)

        # If we can do "pinpoint" highlighting...
        if self.can_load_chars(results, fieldname):
            self.pinpoint_bool = True
            # Build the docnum->[(startchar, endchar),] map
            if fieldname not in results._char_cache:
                self._load_chars(results, fieldname, self.words, to_bytes)

            hitterms = (from_bytes(term[1]) for term in hitobj.matched_terms()
                        if term[0] == fieldname)

            # Grab the word->[(startchar, endchar)] map for this docnum
            cmap = results._char_cache[fieldname][hitobj.docnum]
            # A list of Token objects for matched words
            tokens = []
            charlimit = self.fragmenter.charlimit
            for word in hitterms:
                chars = cmap[word]
                for pos, startchar, endchar in chars:
                    if charlimit and endchar > charlimit:
                        break
                    tokens.append(Token(text=word, pos=pos,
                                        startchar=startchar, endchar=endchar))
            tokens.sort(key=lambda t: t.startchar)
            self.tokens = [max(group, key=lambda t: t.endchar - t.startchar)
                      for key, group in groupby(tokens, lambda t: t.startchar)]
            # fragments = self.fragmenter.fragment_matches(text, tokens)
        else:
            self.pinpoint_bool = False
            # Retokenize the text
            self.analyzer = results.searcher.schema[fieldname].analyzer
            #print("Analyzer: ", type(self.analyzer))
            #print("Analyzer: ", self.analyzer)
            # Analyzer:  CompositeAnalyzer(RegexTokenizer(expression=re.compile('\\w+(\\.?\\w+)*'), gaps=False), LowercaseFilter(), StopFilter(stops=frozenset({'are', 'a', 'for', 'this', 'we', 'us', 'or', 'of', 'be', 'your', 'the', 'if', 'with', 'you', 'at', 'to', 'that', 'will', 'from', 'on', 'yet', 'it', 'as', 'can', 'not', 'in', 'by', 'an', 'is', 'when', 'have', 'may', 'tbd', 'and'}), min=2, max=None, renumber=True)) 

    def highlight_text(self, text, top=3, minscore=1):
        """
        Get the highlights out of the text, using the saved attributes as guide what to search for

        Args:
            text (str): The text
            top (int): How many
            minscore (float): What min score to include

        Return:
            output (str): The highlights
        """

        if self.pinpoint_bool:
            fragments = self.fragmenter.fragment_matches(text, self.tokens)
        else:
            tokens = self.analyzer(text, positions=True, chars=True, mode="index",
                              removestops=False)
            # Set Token.matched attribute for tokens that match a query term
            tokens = set_matched_filter(tokens, self.words)
            tokens = self._merge_matched_tokens(tokens)
            fragments = self.fragmenter.fragment_tokens(text, tokens)

        fragments = top_fragments(fragments, top, self.scorer, self.order,
                                  minscore=minscore)
        output = self.formatter.format(fragments)
        return output