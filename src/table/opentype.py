from fontTools.ttLib import newTable
from fontTools.cffLib import (
    CFFFontSet, TopDict, TopDictIndex, Index,
    PrivateDict, FontDict, FDSelect, CharStrings
)
from src.util.constants import (
    FONT_NAME, VERSION, AUTHOR,
    BOUNDING_BOX, UNITS_PER_EM
)

def create_ot_font_tables(font):
    print("→ 📄 Creating opentype table...")
    cff = font["CFF "] = newTable("CFF ")
    cff_font_set = CFFFontSet()
    top_dict = TopDict(None)
    top_dict_index = TopDictIndex()
    top_dict_index.append(top_dict)
    cff_font_set.topDictIndex = top_dict_index
    cff_font_set.major = 1
    cff_font_set.minor = 0
    cff_font_set.fontNames = [FONT_NAME + "Regular"]
    cff_font_set.GlobalSubrs = Index()

    top_dict.FamilyName = f"{FONT_NAME} Font"
    top_dict.Weight = "Regular"
    top_dict.FullName = f"{FONT_NAME} Font Regular"
    top_dict.version = f"Version {VERSION}"
    top_dict.Notice = f"{FONT_NAME} Font Generation by {AUTHOR}"
    top_dict.FontBBox = BOUNDING_BOX
    top_dict.FontMatrix = [1 / UNITS_PER_EM, 0, 0, 1 / UNITS_PER_EM, 0, 0]

    # Rebuild CharStrings
    private = PrivateDict(None, None, 0)
    #private.defaultWidthX = ADVANCE_WIDTH
    #private.nominalWidthX = 0
    fd_array = [FontDict()]
    fd_array[0].Private = private
    fd_select = FDSelect()
    #global_subrs = Index()
    charstrings = CharStrings(
        None,
        top_dict,
        cff_font_set.GlobalSubrs,
        private,
        fd_select,
        fd_array
    )
    top_dict.Private = private
    top_dict.CharStrings = charstrings
    cff.cff = cff_font_set
