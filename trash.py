def list_all_reaction_index(entries):
    """
    create reaction index without modification, expansion
    maybe no longer useful
    """
    reactionlistdict = {}

    for entnum in entries:
        print(entnum)
        prpcess = Entry(entnum)

        """ create reaction index """
        rindex = prpcess.listreactions()
        if rindex is not None:
            reactionlistdict.update(rindex)

    df = pd.DataFrame.from_dict(reactionlistdict, orient="index")
    # print(df)
    df.to_pickle("pickle/reactions.pickle")


if reac["product"] == "ELEM/MASS":
    data_dict = sub.parse_data()
    mass_index = data_dict["heads"].index("MASS")
    elem_index = data_dict["heads"].index("ELEMENT")

    mass_list = [str(int(float(m))) for m in data_dict["data"][str(mass_index)]]
    charge_list = [str(int(float(m))) for m in data_dict["data"][str(elem_index)]]
    elem_list = [ztoelem(int(float(m))) for m in data_dict["data"][str(elem_index)]]

    try:
        iso_index = data_dict["heads"].index("ISOMER")
        isomer_list = [
            numtoisomer(int(float(m))) for m in data_dict["data"][str(iso_index)]
        ]

        prod_list = [
            charge + "-" + elem + "-" + mass + "-" + iso
            for charge, elem, mass, iso in zip(
                charge_list, elem_list, mass_list, isomer_list
            )
        ]

    except:
        iso_index = None
        data_dict["data"][iso_index] = [None] * len(data_dict["data"][str(elem_index)])
        prod_list = [
            charge + "-" + elem + "-" + mass
            for charge, elem, mass in zip(charge_list, elem_list, mass_list)
        ]

    for prod in prod_list:
        reac["product"] = prod
        df = df.append(reac, ignore_index=True)


elif reac["product"] == "MASS":
    mass_index = data_dict["heads"].index("MASS")
    mass_list = [str(int(float(m))) for m in data_dict["data"][str(mass_index)]]

    for mass in mass_list:
        reac["product"] = "A-" + mass
        df = df.append(reac, ignore_index=True)


elif reac["product"] == "ELEM":
    print(data_dict)
    el_index = data_dict["heads"].index("ELEMENT")
    el_list = [str(int(float(m))) for m in data_dict["data"][str(el_index)]]

    for elem in el_list:
        reac["product"] = "A-" + elem
        df = df.append(reac, ignore_index=True)

else:
    df = df.append(reac, ignore_index=True)


## original stand-alone
def reaction_indexing():
    columndef = [
        "id",
        "entry",
        "subentry",
        "pointer",
        "year",
        "author",
        "target",
        "process",
        "product",
        "branch",
        "sf6",
        "sf7",
        "sf8",
        "sf9",
    ]
    df = pd.DataFrame(columns=columndef)

    reac_set = []
    for entnum in entries:
        print(entnum)
        entry = Entry(entnum)
        main_bib_dict = entry.get_entry_bib_dict()

        """
        indexing of reaction information
        """

        for s in entry.subents_nums:
            reac = {}
            print(s)
            if s == "001":
                main = Subentry(s, entry.entry_body)
                continue
            else:
                sub = Subentry(s, entry.entry_body)

            for pointer, reac in sub.parse_reaction().items():
                if reac["x4code"] is None:
                    continue
                elif (
                    reac["sf6"] == "SIG"
                    and reac["branch"] is None
                    and reac["sf7"] is None
                ):
                    pass
                else:
                    continue

                reac["id"] = entnum + s + pointer
                reac["entry"] = entnum
                reac["subentry"] = s
                reac["pointer"] = pointer
                reac["year"] = main_bib_dict["references"][0]["publication year"]
                reac["author"] = main_bib_dict["authors"][0]["name"]

                del reac["freetext"]
                del reac["x4code"]
                del reac["sf49"]

                """
                product exceptions
                """
                if reac["product"] == "ELEM/MASS":
                    list_dict = {}
                    for x in ["CHARGE", "ELEMENT", "MASS", "ISOMER"]:
                        cil = get_column_index(main, sub, x)
                        list_dict[x] = cil

                    if list_dict["ISOMER"]:
                        prod_list = [
                            charge + "-" + elem + "-" + mass + "-" + iso
                            if iso is not None
                            else charge + "-" + elem + "-" + mass
                            for charge, elem, mass, iso in zip(
                                list_dict["CHARGE"],
                                list_dict["ELEMENT"],
                                list_dict["MASS"],
                                list_dict["ISOMER"],
                            )
                        ]
                    else:
                        prod_list = [
                            charge + "-" + elem + "-" + mass
                            for charge, elem, mass in zip(
                                list_dict["CHARGE"],
                                list_dict["ELEMENT"],
                                list_dict["MASS"],
                            )
                        ]

                    for prod in prod_list:
                        reac["product"] = prod
                        # df = df.append(reac, ignore_index=True)

                elif reac["product"] == "MASS":
                    data_list = get_column_index(main, sub, "MASS")
                    for mass in data_list or []:
                        reac["product"] = "A=" + mass
                        # df = df.append(reac, ignore_index=True)

                elif reac["product"] == "ELEM":
                    data_list = get_column_index(main, sub, "ELEMENT")
                    for elem in data_list or []:
                        reac["product"] = elem
                        # df = df.append(reac, ignore_index=True)

                else:
                    pass

                reac_set.append(reac)

                if len(reac_set) > 100:
                    df = df.from_records(reac_set)
                    print(df)
                    post_many_mongodb("reaction", df.to_dict("records"))
                    df = pd.DataFrame(columns=columndef)

                    print("submitted to mongodb")
                    reac_set = []

    if reac_set:
        df = df.from_records(reac_set)
        print(df)
        post_many_mongodb("reaction", df.to_dict("records"))
        print("submitted to mongodb")
    ## save as a pickle
    # df.to_pickle("pickle/reactions.pickle")

    ## post dataframe to mongodb
    # post_many_mongodb("reaction", df.to_dict('records'))
    return


def view_reaction_index():
    pd.reset_option("display.max_columns")
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1200)
    with open("pickle/reactions.pickle", "rb") as pkl:
        df = pd.read_pickle(pkl)
    # print(df)
    sf9 = df[(df["sf9"] != "") & (df["code"] != "Ratio")]
    print(sf9)
    return
