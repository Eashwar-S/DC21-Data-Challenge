import pandas as pds
import numpy as np
import matplotlib.pyplot as plt
import operator

"""
    Function to read data from the excel sheet.
"""


def readData():
    file = '../dataset/Data_Lv2_USDA_PackagedMeals.xls'
    newData = pds.read_excel(file)
    return newData


"""
    Function to determine all the food categories from excel sheet.
"""


def foodCategories(newData):
    food_Categories = []
    countFoodCategories = {}
    for food_categories in newData['branded_food_category']:
        food_Categories.append(food_categories)

    food_Categories = list(set(food_Categories))
    for cat in newData['branded_food_category']:
        if cat in food_Categories:
            if cat in countFoodCategories.keys():
                countFoodCategories[cat] += 1
            else:
                countFoodCategories[cat] = 1
    return food_Categories, countFoodCategories


"""
    Convert all the ingredients in list for easy processing.
"""


def processfoodIngredients(ingredients):
    openBrackets = ['[', '{', '(']
    closeBrackets = [']', '}', ')']
    processedIngredients = []
    for k in range(len(ingredients)):
        if isinstance(ingredients[k], str):
            ingredients[k] = ingredients[k].lower()
            i = 0
            while i < len(ingredients[k]):
                if ingredients[k][i] in openBrackets:
                    startIndex = openBrackets.index(ingredients[k][i])
                    for j in range(i + 1, len(ingredients[k])):
                        if ingredients[k][j] == closeBrackets[startIndex]:
                            ingredients[k] = ingredients[k][:i] + ingredients[k][j + 1:]
                            break
                i += 1
            if ingredients[k].find('CONTAINS') != -1:
                startIndex = ingredients[k].index('CONTAINS')
                for p in range(startIndex + 1, len(ingredients[k])):
                    if ingredients[k][p] == ":":
                        ingredients[k] = ingredients[k][:startIndex] + ingredients[k][p + 1:]
                        break

            if '.' in ingredients[k]:
                index = ingredients[k].index('.')
                if index != len(ingredients[k]) - 1:
                    ingredients[k] = ingredients[k][:index] + ',' + ingredients[k][index + 1:]
                else:
                    ingredients[k] = ingredients[k][:index]

            processedIngredients.append([i.strip() for i in ingredients[k].split(",")])
        else:
            processedIngredients.append([])

    return processedIngredients


"""
    Function to determine ingredients of the food from excel sheet.
"""


def popularFoodIngredients(newData, foodCategories):
    ingredients = []
    for ingre in newData['ingredients']:
        ingredients.append(ingre)

    processedIngredients = processfoodIngredients(ingredients)
    ingreCount = {}
    ingreCountTotal = {}
    for cate in foodCategories:
        ingreCount[cate] = {}
    i = 0
    for j in range(len(processedIngredients)):
        for k in range(len(processedIngredients[j])):
            if processedIngredients[j][k] in ingreCount[newData['branded_food_category'][j]].keys():
                ingreCount[newData['branded_food_category'][j]][processedIngredients[j][k]] += 1
            else:
                ingreCount[newData['branded_food_category'][j]][processedIngredients[j][k]] = 1

            if processedIngredients[j][k] in ingreCountTotal.keys():
                ingreCountTotal[processedIngredients[j][k]] += 1
            else:
                ingreCountTotal[processedIngredients[j][k]] = 1

    return ingreCount, ingreCountTotal


def convertToPercentage(ingreCount, ingreCountTotal, countFoodCategories):
    for key, county in ingreCount.items():
        sum1 = countFoodCategories[key]
        for k, value in county.items():
            if value > sum1:
                print(value, sum1, k)
            county[k] = (value / sum1) * 100
            if county[k] > 100:
                county[k] = 100

    for ingredient in ingreCountTotal.keys():
        ingreCountTotal[ingredient] = (ingreCountTotal[ingredient] / 4437) * 100

    return ingreCount, ingreCountTotal


def plotData(ingreCount, ingreCountTotal):
    for county in ingreCount.keys():
        sortedDict = dict(sorted(ingreCount[county].items(), key=operator.itemgetter(1), reverse=True))
        objects = list(sortedDict.keys())
        y_pos = np.arange(len(objects))

        performance = list(sortedDict.values())
        # performance.sort(reverse=True)

        plt.barh(y_pos[:30], performance[:30], align='center', alpha=1)
        plt.yticks(y_pos[:30], objects[:30])
        plt.ylabel('Top ' + str(15) + ' Ingredients')
        plt.xlabel('% usage of ingredients')
        # plt.pie(performance[:15], labels=objects[:15])
        plt.title('Popular Ingredients in ' + county + " category")
        plt.show()

    sortedDict = dict(sorted(ingreCountTotal.items(), key=operator.itemgetter(1), reverse=True))
    objects = list(sortedDict.keys())
    y_pos = np.arange(len(objects))

    performance = list(sortedDict.values())
    # performance.sort(reverse=True)

    plt.barh(y_pos[:15], performance[:15], align='center', alpha=1)
    plt.yticks(y_pos[:15], objects[:15])
    plt.ylabel('Top ' + str(15) + ' Ingredient')
    plt.xlabel('% usage of ingredients')
    # plt.pie(performance[:15], labels=objects[:15])
    plt.title('Popular Ingredients in all category')

    plt.show()


newData = readData()
categories, countFoodCategories = foodCategories(newData)
ingreCount, ingreCountTotal = popularFoodIngredients(newData, categories)
ingreCount, ingreCountTotal = convertToPercentage(ingreCount, ingreCountTotal, countFoodCategories)
plotData(ingreCount, ingreCountTotal)
