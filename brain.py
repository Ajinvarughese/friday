import services
import importlib


def add_function(code: str =""):
    with open("services.py", "a") as f:
        f.write(code)



def generateAiMethod():

    while True:
        fName = input("Enter function: ")

        if fName == "div":
            add_function(
                """
                def div_func(a, b):
                    if b == 0:
                        return "Cannot divide by zero"
                    return a / b
                """
            )   # 👈 write to file

        importlib.reload(services)

        # get function directly
        dynamic_func = getattr(services, f"{fName}_func", None)

        if dynamic_func:
            print(dynamic_func(6, 3))
        else:
            print("Function not found")