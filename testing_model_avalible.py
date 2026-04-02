import google.generativeai as genai

genai.configure(api_key="AIzaSyA99aTsHF25K0JKY-uwXpwBCvAfUraN8cs")
for model in genai.list_models():
    print(model.name)