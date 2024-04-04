from ImageFinder.ImageFinder import get_images_links as find_image
from VideoFinder.VideoFinder import search_videos_by_keyword
from KNN_model import output_recommended_recipes, recommend
from LinkGenerator.LinkGenerator import generate_links
from TimeReformation.TimeReformation import iso8601_to_normal
from streamlit_echarts import st_echarts
from dataset.data import food_dataframe
import streamlit as st
import pandas as pd
from PIL import Image


st.set_page_config(page_title="EasyMeal", page_icon="🍴", layout="wide")
nutrition_values = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent',
                    'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']

if 'generated' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations = None


class Recommendation:
    def __init__(self, dataset, nutrition_list, nb_recommendations, ingredient_txt):
        self.nutrition_list = nutrition_list
        self.nb_recommendations = nb_recommendations
        self.ingredient_txt = ingredient_txt
        self.dataset = dataset
        pass

    def generate(self, ):
        params = {'n_neighbors': self.nb_recommendations, 'return_distance': False}
        ingredients = self.ingredient_txt.split(';')
        raw_recommend = recommend(self.dataset, self.nutrition_list, ingredients, params)
        recommendations = output_recommended_recipes(raw_recommend)
        if recommendations != None:
            for recipe in recommendations:
                recipe['image_link'] = find_image(recipe['Name'])
        return recommendations, ingredients


class Display:
    def __init__(self):
        self.nutrition_values = nutrition_values

    def display_recommendation(self, recommendations, user_ingredients):
        st.subheader('Recommended recipes:')
        if recommendations != None:
            rows = len(recommendations) // 5
            for column, row in zip(st.columns(5), range(5)):
                with column:
                    for recipe in recommendations[rows * row:rows * (row + 1)]:
                        recipe_name = recipe['Name']
                        expander = st.expander(recipe_name)
                        recipe_link = recipe['image_link']
                        recipe_img = f'<div><center><img src={recipe_link} alt={recipe_name}></center></div>'
                        nutritions_df = pd.DataFrame({value: [recipe[value]] for value in nutrition_values})

                        expander.markdown(recipe_img, unsafe_allow_html=True)
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values (g):</h5>',
                            unsafe_allow_html=True)
                        expander.dataframe(nutritions_df)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Tutorial:</h5>',
                                          unsafe_allow_html=True)

                        expander.markdown(search_videos_by_keyword(recipe_name), unsafe_allow_html=True)

                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Ingredients:</h5>',
                                          unsafe_allow_html=True)
                        for ingredient in recipe['RecipeIngredientParts']:
                            expander.markdown(f"""
                                        - {ingredient}
                            """)

                        links, products = generate_links(recipe['RecipeIngredientParts'], user_ingredients)
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">Missing products:</h5>',
                            unsafe_allow_html=True)
                        for i  in range(0, len(products)):
                            expander.markdown(f" [{products[i]}](%s)" % links[i], unsafe_allow_html=True)

                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">Recipe Instructions:</h5>',
                            unsafe_allow_html=True)
                        for instruction in recipe['RecipeInstructions']:
                            expander.markdown(f"""
                                        - {instruction}
                            """)
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">Cooking and Preparation Time:</h5>',
                            unsafe_allow_html=True)
                        expander.markdown(f"""
                                - Cook Time       : {iso8601_to_normal(recipe['CookTime'])}min
                                - Preparation Time: {iso8601_to_normal(recipe['PrepTime'])}min
                                - Total Time      : {iso8601_to_normal(recipe['TotalTime'])}min
                            """)
        else:
            st.info('Couldn\'t find any recipes with the specified ingredients', icon="🥲")

    def display_overview(self, recommendations):
        if recommendations != None:
            st.subheader('Overview:')
            col1, col2, col3 = st.columns(3)
            with col2:
                selected_recipe_name = st.selectbox('Select a recipe', [recipe['Name'] for recipe in recommendations])
            st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values:</h5>',
                        unsafe_allow_html=True)
            for recipe in recommendations:
                if recipe['Name'] == selected_recipe_name:
                    selected_recipe = recipe
            options = {
                "title": {"text": "Nutrition values", "subtext": f"{selected_recipe_name}", "left": "center"},
                "tooltip": {"trigger": "item"},
                "legend": {"orient": "vertical", "left": "left", },
                "series": [
                    {
                        "name": "Nutrition values",
                        "type": "pie",
                        "radius": "50%",
                        "data": [{"value": selected_recipe[nutrition_value], "name": nutrition_value} for
                                 nutrition_value in self.nutrition_values],
                        "emphasis": {
                            "itemStyle": {
                                "shadowBlur": 10,
                                "shadowOffsetX": 0,
                                "shadowColor": "rgba(0, 0, 0, 0.5)",
                            }
                        },
                    }
                ],
            }
            st_echarts(options=options, height="600px", )
            st.caption('You can select/deselect an item (nutrition value) from the legend.')


hide_st_style = """
            <style>
            
            footer {visibility: hidden;}
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}

            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
left_co, cent_co,last_co = st.columns(3)
with cent_co:
    st.image(Image.open('icon.png'))

title = "<h1 style='text-align: center;'>EasyMeal recommendation</h1>"
st.markdown(title, unsafe_allow_html=True)

display = Display()

with st.form("recommendation_form"):
    ingredient_txt = st.text_input('Write down your ingredients separating them with a ";" :',
                                   placeholder='Ingredient1;Ingredient2;...')
    st.caption('E.g.: chicken;eggs;butter;...')
    st.header('Nutritional values:')
    Calories = st.slider('Calories', 0, 2000, 500)
    FatContent = st.slider('FatContent', 0, 100, 50)
    SaturatedFatContent = st.slider('SaturatedFatContent', 0, 13, 0)
    CholesterolContent = st.slider('CholesterolContent', 0, 300, 0)
    SodiumContent = st.slider('SodiumContent', 0, 2300, 400)
    CarbohydrateContent = st.slider('CarbohydrateContent', 0, 325, 100)
    FiberContent = st.slider('FiberContent', 0, 50, 10)
    SugarContent = st.slider('SugarContent', 0, 40, 10)
    ProteinContent = st.slider('ProteinContent', 0, 40, 10)
    nutritions_values_list = [Calories, FatContent, SaturatedFatContent, CholesterolContent, SodiumContent,
                              CarbohydrateContent, FiberContent, SugarContent, ProteinContent]
    st.header('Recommendation options:')
    nb_recommendations = st.slider('Number of recipes', 5, 20, step=5)
    generated = st.form_submit_button("Generate")
if generated:
    with st.spinner('Generating recommendations...'):
        recommendation = Recommendation(food_dataframe, nutritions_values_list, nb_recommendations, ingredient_txt)
        recommendations, user_ingredients = recommendation.generate()
        st.session_state.recommendations = recommendations
        st.session_state.user_ingredients = user_ingredients
    st.session_state.generated = True

if st.session_state.generated:
    with st.container():
        display.display_recommendation(st.session_state.recommendations, st.session_state.user_ingredients)
    with st.container():
        display.display_overview(st.session_state.recommendations)
