from googletrans import Translator


def translate_to_russian(words):
    translator = Translator()
    words = [translator.translate(word, src='en', dest='ru').text for word in words]
    return words


def find_missing_products(all_products, available_products):
    missing_products = []
    for product in all_products:
        if product not in available_products:
            missing_products.append(product)
    return missing_products


def generate_links(ingredients, user_ingredients):
    products = find_missing_products(ingredients, user_ingredients)
    translated_products = translate_to_russian(products)
    base_url = "https://astykzhan.kz/search/index.php?q="
    links = []
    for product in translated_products:
        formatted_product = "+".join(product.split())
        link = base_url + formatted_product + "&s="
        links.append(link)
    return links, products
