import matplotlib.pyplot as plt


#This function takes in the reference values and the prediction values as lists and returns a list with each index corresponding to the total number
#of points within that zone (0=A, 1=B, 2=C, 3=D, 4=E) and the plot
def clarke_error_grid(ref_values, pred_values, title_string):

    #Checking to see if the lengths of the reference and prediction arrays are the same
    assert (len(ref_values) == len(pred_values)), "Unequal number of values (reference : {}) (prediction : {}).".format(len(ref_values), len(pred_values))

    #Checks to see if the values are within the normal physiological range, otherwise it gives a warning
    if max(ref_values) > 400 or max(pred_values) > 400:
        print ("Input Warning: the maximum reference value {} or the maximum prediction value {} exceeds the normal physiological range of glucose (<400 mg/dl).".format(max(ref_values), max(pred_values)))
    if min(ref_values) < 0 or min(pred_values) < 0:
        print ("Input Warning: the minimum reference value {} or the minimum prediction value {} is less than 0 mg/dl.".format(min(ref_values),  min(pred_values)))

    #Clear plot
    plt.clf()
    ax = plt.gca()
    bwith = 3
    #ax.spines['top'].set_color('red')  # 设置上‘脊梁’为红色
    #ax.spines['right'].set_color('none')  # 设置上‘脊梁’为无色
    ax.spines['bottom'].set_linewidth(bwith)
    ax.spines['left'].set_linewidth(bwith)
    ax.spines['top'].set_linewidth(bwith)
    ax.spines['right'].set_linewidth(bwith)

    #Set up plot
    plt.scatter(ref_values, pred_values, marker='o', color='black', s=8)
    plt.title(title_string + " Clarke Error Grid", fontdict={'family' : 'Arial', 'size'   : 22})
    plt.xlabel("Reference Concentration (mg/dl)", fontdict={'family' : 'Arial', 'size'   : 22})
    plt.ylabel("Prediction Concentration (mg/dl)", fontdict={'family' : 'Arial', 'size'   : 22})
    plt.xticks([0, 100,  200, 300, 400], fontsize=22)
    plt.yticks([0, 100,  200, 300, 400], fontsize=22)
    plt.gca().set_facecolor('white')

    #Set axes lengths
    plt.gca().set_xlim([0, 400])
    plt.gca().set_ylim([0, 400])
    plt.gca().set_aspect((400)/(400))

    #Plot zone lines
    a = 3
    plt.plot([0,400], [0,400], ':', c='black', linewidth=a)                      #Theoretical 45 regression line
    plt.plot([0, 175/3], [70, 70], '-', c='black', linewidth=a)
    #plt.plot([175/3, 320], [70, 400], '-', c='black')
    plt.plot([175/3, 400/1.2], [70, 400], '-', c='black', linewidth=a)           #Replace 320 with 400/1.2 because 100*(400 - 400/1.2)/(400/1.2) =  20% error
    plt.plot([70, 70], [84, 400],'-', c='black', linewidth=a)
    plt.plot([0, 70], [180, 180], '-', c='black', linewidth=a)
    plt.plot([70, 290],[180, 400],'-', c='black', linewidth=a)
    # plt.plot([70, 70], [0, 175/3], '-', c='black')
    plt.plot([70, 70], [0, 56], '-', c='black', linewidth=a)                     #Replace 175.3 with 56 because 100*abs(56-70)/70) = 20% error
    # plt.plot([70, 400],[175/3, 320],'-', c='black')
    plt.plot([70, 400], [56, 320],'-', c='black', linewidth=a)
    plt.plot([180, 180], [0, 70], '-', c='black', linewidth=a)
    plt.plot([180, 400], [70, 70], '-', c='black', linewidth=a)
    plt.plot([240, 240], [70, 180],'-', c='black', linewidth=a)
    plt.plot([240, 400], [180, 180], '-', c='black', linewidth=a)
    plt.plot([130, 180], [0, 70], '-', c='black', linewidth=a)

    #Add zone titles
    plt.text(30, 15, "A", fontsize=25)
    plt.text(370, 260, "B", fontsize=25)
    plt.text(280, 360, "B", fontsize=25)
    plt.text(145, 360, "C", fontsize=25)
    plt.text(150, 5, "C", fontsize=25)
    plt.text(30, 140, "D", fontsize=25)
    plt.text(370, 120, "D", fontsize=25)
    plt.text(30, 360, "E", fontsize=25)
    plt.text(365, 15, "E", fontsize=25)

    #Statistics from the data
    zone = [0] * 5
    for i in range(len(ref_values)):
        if (ref_values[i] <= 70 and pred_values[i] <= 70) or (pred_values[i] <= 1.2*ref_values[i] and pred_values[i] >= 0.8*ref_values[i]):
            zone[0] += 1    #Zone A

        elif (ref_values[i] >= 180 and pred_values[i] <= 70) or (ref_values[i] <= 70 and pred_values[i] >= 180):
            zone[4] += 1    #Zone E

        elif ((ref_values[i] >= 70 and ref_values[i] <= 290) and pred_values[i] >= ref_values[i] + 110) or ((ref_values[i] >= 130 and ref_values[i] <= 180) and (pred_values[i] <= (7/5)*ref_values[i] - 182)):
            zone[2] += 1    #Zone C
        elif (ref_values[i] >= 240 and (pred_values[i] >= 70 and pred_values[i] <= 180)) or (ref_values[i] <= 175/3 and pred_values[i] <= 180 and pred_values[i] >= 70) or ((ref_values[i] >= 175/3 and ref_values[i] <= 70) and pred_values[i] >= (6/5)*ref_values[i]):
            zone[3] += 1    #Zone D
        else:
            zone[1] += 1    #Zone B

    return plt, zone


import pandas as pd

data = pd.read_csv('./clark_solar.csv')

data.shape #(342, 12)
True_value = data.iloc[:, 1]  # data
Predict = data.iloc[:, 3]   # label
clarke_error_grid(True_value, Predict, 'solar')
plt.show()
