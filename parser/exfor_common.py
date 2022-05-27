def test():
    f = None
    print("case 1: \n")

    if not f:
        f = None
        print("   1")
        if not f:
            f = None
            print("   2")
            if not None:
                f = None
                print("   3")
