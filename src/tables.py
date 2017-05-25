
class Table:
    """
    This class represents data arranged into a grid
    Use this class to render textual data and print it to stdout
    """

    def __init__(self):
        self.data = []
        self.columns = []

    def addColumn(self, name, key, format = "%s"):
        self.columns.append({"name": name, "key": key, "format": format})

    def render(self, width = 80):
        self._width = width
        rendered_data = [[]]

        # render headers:
        mxwidth = []
        for column in self.columns:
            rendered_data[0].append(column["name"])
            mxwidth.append(len(column["name"]))

        # render data
        i = 0
        for row in self.data:
            i += 1
            rendered_data.append([])
            for j, column in enumerate(self.columns):
                if callable(column["key"]):
                    data = column["key"](row)
                else:
                    data = row[column["key"]]

                if callable(column["format"]):
                    strdata = column["format"](data)
                else:
                    strdata = column["format"] % data

                rendered_data[i].append(strdata)
                mxwidth[j] = max(mxwidth[j], len(strdata))

        # render table
        # padding := 2
        nl = "\r\n"
        separator_line = "+" + "+".join("-" * (ln + 2) for ln in mxwidth) + "+" + nl
        rendered_text = ""
        rendered_text += separator_line
        for row in rendered_data:
            rendered_text += "|"
            for j, column in enumerate(row):
                spaces = " " * (mxwidth[j] - len(column) + 1)
                rendered_text += spaces + column + " |"
            rendered_text += nl + separator_line
        return rendered_text
