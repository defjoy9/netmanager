


def joy(aaaaaaaaaaaaaaaa):
    try:
        if aaaaaaaaaaaaaaaa > 1:
            print(f"{aaaaaaaaaaaaaaaa} is bigger than 1")
            return 1
        else:
            print(f"{aaaaaaaaaaaaaaaa} is not bigger than 1")
            return 1
    except Exception as e:
        print(f"An exception occured: {e}")
        raise


num = "ASD"

joy(num)