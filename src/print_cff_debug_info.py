from fontTools.cffLib import CFFFontSet

def print_cff_debug_info(font):
    from fontTools.ttLib.tables import C_F_F_

    print("\n🔍 CFF Table Debug Info")
    print("=" * 30)

    cff_table = font["CFF "]
    assert isinstance(cff_table, C_F_F_.table_C_F_F_), "❌ CFF table is not a proper wrapper"
    assert hasattr(cff_table, "cff"), "❌ CFF table missing .cff attribute"
    assert isinstance(cff_table.cff, CFFFontSet), "❌ CFF table .cff is not a CFFFontSet"

    cff = cff_table.cff
    print(f"→ CFFFontSet: {cff}")
    print(f"→ Number of TopDicts: {len(cff.topDictIndex)}")

    for i, top_dict in enumerate(cff.topDictIndex):
        print(f"\n📂 TopDict #{i}")
        print("-" * 20)
        print(f"  FamilyName:   {getattr(top_dict, 'FamilyName', '❌')}")
        print(f"  FullName:     {getattr(top_dict, 'FullName', '❌')}")
        print(f"  FontBBox:     {getattr(top_dict, 'FontBBox', '❌')}")
        print(f"  FontMatrix:   {getattr(top_dict, 'FontMatrix', '❌')}")
        print(f"  Version:      {getattr(top_dict, 'Version', '❌')}")
        print(f"  Notice:       {getattr(top_dict, 'Notice', '❌')}")

        if hasattr(top_dict, "Private"):
            print("\n🔧 PrivateDict:")
            for key, val in vars(top_dict.Private).items():
                if not key.startswith("_"):
                    print(f"  {key}: {val}")
        else:
            print("  ❌ No PrivateDict")

        if hasattr(top_dict, "CharStrings"):
            charstrings = top_dict.CharStrings
            print(f"\n✒️  CharStrings (glyphs): {len(charstrings)}")
            for name in list(charstrings.keys())[:5]:
                cs = charstrings[name]
                width = getattr(cs, "width", "unknown")
                print(f"  - {name}: width={width}")
            if len(charstrings) > 5:
                print("  ...")
        else:
            print("  ❌ No CharStrings found")

        if hasattr(top_dict, "FDArray"):
            print(f"\n🗃️  FDArray: {len(top_dict.FDArray)} entries")
        if hasattr(top_dict, "FDSelect"):
            print(f"🔢 FDSelect: {top_dict.FDSelect}")

    print("=" * 30 + "\n")
