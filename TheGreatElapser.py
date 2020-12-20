#Python Script to make csv file and determine time elapse between each photo for singular folder
# 12/14/2020

import csv
import os
from datetime import datetime
import multiprocessing
import argparse

#Reads in all .png files in current working directory and returns the filenames in a list
def readinPhotos():
    #mypath = path
    mypath = os.getcwd() #getting path to directory
    files = [f for f in os.listdir(mypath) if f.endswith(".png")] #finding files
    files.sort(key=os.path.getctime) #sort by creation time to be in order
    #for file in files:
        #print(file)
    return files

#Takes in two dates, earlier one first. Finds the difference between the time and returns it
def findElapseTime(first, second):
    d1 = datetime.strptime(first, '%Y-%m-%d--%H-%M-%S')
    d2 = datetime.strptime(second, '%Y-%m-%d--%H-%M-%S')
    difference = d2 - d1
    return difference

#Takes in data structure of results and writes it to a csv file
def writeCSV(data):
    # writing csv file
    with open('time_elapsed.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for line in data:
            num = line[0]
            original = line[1]
            elapse = line[2]
            writer.writerow([num, original, elapse])

# Function taking in first photo date, the list of photo file names, length of that list (to find number of photos),
# and data dictionary for storing the results. Returns the data structure
def timeElapsed(firstDate, photoList, length, data):
    for i in range(1, length):
        original_time = photoList[i]
        original_time = original_time.split('_')[0]  # slicing down just to date

        #time since start
        elapseTime_first = findElapseTime(firstDate, original_time)
        elapseTime_first_sec = elapseTime_first.total_seconds()
        elapseTime_first_hours = divmod(elapseTime_first_sec, 3600)[0]

        data.append([i, original_time, elapseTime_first_hours])

    return data

def Elapse(path):
    os.chdir(path)

    #read in the photos from the folder to a data structure
    photoList = readinPhotos()

    #go one by one and find the time lapse elapse time and write into csv file
    length = len(photoList)
    data = [('Photo Number', 'Original Time Taken', 'Time Elapsed From Start')] #headers of columns
    data.append([0, photoList[0].split('_')[0], 0]) #first photo
    firstDate = photoList[0].split('_')[0] #getting date of first photo to comapre to other photos

    data = timeElapsed(firstDate, photoList, length, data)

    #writing csv file
    writeCSV(data)

def main():
    #argument parser and parsing
    parser = argparse.ArgumentParser(description='Take directory of position directories from experiment '
                                                 'and find the time since first photo of experiment')

    parser.add_argument('--path', '-p', type=str, help='Path to folder to execute', required=True)
    parser.add_argument('--single', '-s', action='store_true', help='Add this option to just create csv from single folder from provided path')
    parser.add_argument('--multi', '-m', action='store_true', help='This flag will use multi-processing on the script. Only needed for large number of position folders')

    args = parser.parse_args()

    #change path is provided
    if args.path is not None:
        os.chdir(args.path)

    # if single folder csv argument passed
    # then do single folder sequential
    if args.single is True:
        Elapse(os.getcwd())
        exit()

    #getting the position folders from main directory
    contents = os.listdir()
    dir = os.getcwd() #main directory provided
    positionFolders = []

    # otherwise start going through the entire folder of position folders
    # setting up processes
    processes = list()
    threads = list()
    for folder in contents:
        if "Position" in folder:
            folder_path = os.path.join(dir, folder)
            positionFolders.append(folder_path)
        else:
            print('Check given path again that it includes position folders')
            exit()

    #multiprocessing
    if args.multi is True:
        with multiprocessing.Pool() as pool:
            pool.map(Elapse, positionFolders)
            pool.close()
            pool.join()

    #sequential process
    for i in range(len(positionFolders)):
        try:
            Elapse(positionFolders[i])
        except:
            print(f"Program failed to process elapse time for folder {positionFolders[i]}")

    #To mark that program was successful
    print("The program was successful")

if __name__ == "__main__":
    main()
