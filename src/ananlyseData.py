import pandas as pds
import numpy as np
import matplotlib.pyplot as plt
import operator

"""
    Function to read ingredients data from the excel sheet.
"""


def readIngredientsData():
    file = '../dataset/Data_Lv2_USDA_PackagedMeals.xls'
    newData = pds.read_excel(file)
    return newData


"""
    Function to read nutrients data from the excel sheet.
"""


def readNutrientsData():
    file = '../dataset/food_nutrient.csv'
    file1 = '../dataset/nutrient.xls'
    newData1 = pds.read_csv(file, low_memory=False)
    newData2 = pds.read_excel(file1)
    return newData1, newData2


def determineNutrientsForFood(newData, newData1):
    nutrientID = []
    nutrientAmount = []
    index = 0
    for i, fdc_id in enumerate(newData['fdc_id']):
        try:
            index = list(newData1['fdc_id']).index(fdc_id)
        except ValueError:
            nutrientID.append(0)
            nutrientAmount.append(0)
        nutrientID.append(newData1['nutrient_id'][index])
        nutrientAmount.append(newData1['amount'][index])
        print(i)
    np.save('nutrientID', np.array(nutrientID))
    np.save('nutrientAmount', np.array(nutrientAmount))


def nutrientsInfo(newData, nutrientID):
    # nutrientAmount = list(np.load('../dataset/nutrientAmount.npy'))

    nutrientsPresent = []
    nutrientsRanking = []
    index = 0
    for i, id in enumerate(nutrientID):
        try:
            index = list(newData['id']).index(id)
        except ValueError:
            nutrientsPresent.append(0)
            nutrientsRanking.append(0)
        nutrientsPresent.append(newData['name'][index])
        nutrientsRanking.append(newData['rank'][index])
        print(i)
    np.save('../dataset/nutrientsPresent', np.array(nutrientsPresent))
    np.save('../dataset/nutrientsRankings', np.array(nutrientsRanking))


def nutrientsRankings(newData, nutrientRanking):
    rank = {}
    for i, category in enumerate(newData['branded_food_category']):
        rank[category] = nutrientRanking[i]

    sortedDict = dict(sorted(rank.items(), key=operator.itemgetter(1), reverse=True))
    return sortedDict


def nutrientsAmount(newData, nutrientAmount):
    amount = {}
    for i, category in enumerate(newData['branded_food_category']):
        amount[category] = nutrientAmount[i]

    sortedDict = dict(sorted(amount.items(), key=operator.itemgetter(1), reverse=True))
    return sortedDict


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
    ingCount = {}
    ingCountTotal = {}
    for cate in foodCategories:
        ingCount[cate] = {}

    for j in range(len(processedIngredients)):
        for k in range(len(processedIngredients[j])):
            if processedIngredients[j][k] in ingCount[newData['branded_food_category'][j]].keys():
                ingCount[newData['branded_food_category'][j]][processedIngredients[j][k]] += 1
            else:
                ingCount[newData['branded_food_category'][j]][processedIngredients[j][k]] = 1

            if processedIngredients[j][k] in ingCountTotal.keys():
                ingCountTotal[processedIngredients[j][k]] += 1
            else:
                ingCountTotal[processedIngredients[j][k]] = 1

    return ingCount, ingCountTotal


"""
    Function to determine percentage usage of ingredients in each category and as a whole.
"""


def convertToPercentage(ingCount, ingCountTotal, countFoodCategories):
    for key, county in ingCount.items():
        sum1 = countFoodCategories[key]
        for k, value in county.items():
            county[k] = (value / sum1) * 100
            if county[k] > 100:
                county[k] = 100

    for ingredient in ingCountTotal.keys():
        ingCountTotal[ingredient] = (ingCountTotal[ingredient] / 4437) * 100

    return ingCount, ingCountTotal


"""
    Function to represent top 15 popular ingredients in each category and as a whole.
"""


def plotIngredientsData(ingCount, ingCountTotal):
    for county in ingCount.keys():
        sortedDict = dict(sorted(ingCount[county].items(), key=operator.itemgetter(1), reverse=True))
        objects = list(sortedDict.keys())
        y_pos = np.arange(len(objects))

        performance = list(sortedDict.values())
        # performance.sort(reverse=True)

        plt.barh(y_pos[:15], performance[:15], align='center', alpha=1)
        plt.yticks(y_pos[:15], objects[:15])
        plt.ylabel('Top ' + str(15) + ' popular ingredients')
        plt.xlabel('% usage of ingredients')
        # plt.pie(performance[:15], labels=objects[:15])
        plt.title('Popular Ingredients in ' + county + " category")
        plt.show()

    sortedDict = dict(sorted(ingCountTotal.items(), key=operator.itemgetter(1), reverse=True))
    objects = list(sortedDict.keys())
    y_pos = np.arange(len(objects))

    performance = list(sortedDict.values())
    # performance.sort(reverse=True)

    plt.barh(y_pos[:15], performance[:15], align='center', alpha=1)
    plt.yticks(y_pos[:15], objects[:15])
    plt.ylabel('Top ' + str(15) + ' popular ingredients')
    plt.xlabel('% usage of ingredients')
    # plt.pie(performance[:15], labels=objects[:15])
    plt.title('Popular Ingredients in all category')

    plt.show()


"""
    Function to plot quality of nutrients in each food category. 
"""


def plotNutrientsRankingData(rank):
    objects = list(rank.keys())
    y_pos = np.arange(len(objects))

    performance = list(rank.values())
    # performance.sort(reverse=True)

    plt.barh(y_pos[:15], performance[:15], align='center', alpha=1)
    plt.yticks(y_pos[:15], objects[:15])
    plt.xlabel('Ranking level')
    # plt.pie(performance[:15], labels=objects[:15])
    plt.title('High quality nutritious food category ranking')
    plt.show()


"""
    Function to plot amount of nutrients in each food category. 
"""


def plotNutrientsAmountData(amount):
    objects = list(amount.keys())
    y_pos = np.arange(len(objects))

    performance = list(amount.values())
    # performance.sort(reverse=True)

    plt.barh(y_pos[:15], performance[:15], align='center', alpha=1)
    plt.yticks(y_pos[:15], objects[:15])
    plt.xlabel('Nutrients Amount')
    # plt.pie(performance[:15], labels=objects[:15])
    plt.title('Nutritious rich food categories ranking')
    plt.show()


"""
    Function to plot a pie chart of quantity of foods in each food category. 
"""


def plotCategories(countFoodCategories):
    categories = list(countFoodCategories.keys())

    numberOfFoods = list(countFoodCategories.values())

    # Wedge properties
    wp = {'linewidth': 1, 'edgecolor': "green"}

    def func(pct, allvalues):
        absolute = int(pct / 100. * np.sum(allvalues))
        return "{:.1f}%\n({:d})".format(pct, absolute)

    fig, ax = plt.subplots(figsize=(10, 7))
    wedges, texts, autotexts = ax.pie(numberOfFoods,
                                      autopct=lambda pct: func(pct, numberOfFoods),
                                      shadow=True,
                                      startangle=90,
                                      wedgeprops=wp,
                                      textprops=dict(color="black"))

    ax.legend(wedges, categories,
              title="Food Categories",
              loc="upper left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    plt.setp(autotexts, size=8, weight="bold")
    ax.set_title("Branded Food Categories Pie Chart")
    plt.show()


def main():
    newData = readIngredientsData()
    # newData1, newData2 = readNutrientsData()
    categories, countFoodCategories = foodCategories(newData)
    plotCategories(countFoodCategories)
    ingCount, ingCountTotal = popularFoodIngredients(newData, categories)
    ingCount, ingCountTotal = convertToPercentage(ingCount, ingCountTotal, countFoodCategories)
    plotIngredientsData(ingCount, ingCountTotal)
    nutrientRankings = list(np.load('../dataset/nutrientsRankings.npy'))
    nutrientAmount = list(np.load('../dataset/nutrientAmount.npy'))
    rank = nutrientsRankings(newData, nutrientRankings)
    amount = nutrientsAmount(newData, nutrientAmount)
    plotNutrientsRankingData(rank)
    plotNutrientsAmountData(amount)


if __name__ == "__main__":
    main()
