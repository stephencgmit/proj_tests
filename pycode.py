import pymongo
from pymongo import MongoClient
from pyfingerprint.pyfingerprint import PyFingerprint
import datetime
import tempfile
import hashlib
import time

client = MongoClient("mongodb://fpDBuser:project2019@fingerprintproject-shard-00-00-2ee1v.mongodb."
                     "net:27017,fingerprintproject-shard-00-01-2ee1v.mongodb.net:27017,"
                     "fingerprintproject-shard-00-02-2ee1v.mongodb.net:27017/test?ssl=true&replicaSet="
                     "FingerprintProject-shard-0&authSource=admin&retryWrites=true")

mydb = client['fingerprint_project']
coll = mydb['students']
login_fails = 0

def login1():
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)

    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    time.sleep(1)
    try:
        while ( f.readImage() == False ):
            pass
        f.convertImage(0x01)
        result = f.searchTemplate() ## Searchs template
        positionNumber = result[0]
        accuracyScore = result[1]
    
        if ( positionNumber == -1 ):
            print('No match found! Try again')
            time.sleep(0.5)
            #login()
        else:
            print('Found template at position #' + str(positionNumber))
            print('The accuracy score is: ' + str(accuracyScore))
            temp = positionNumber
            #return 0
    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)
    
    if ( positionNumber == -1 ):
        print('No match found! Try again')
        #global login_fails
        #login_fails=login_fails+1
        #time.sleep(0.5)
        #print('login_fails' + str(login_fails))
        #if(login_fails <= 3):
        #    print("Login Attempt: #" + str(login_fails))
            #login1()
        print("Fingerprint login failed")
        return -1
    else:
        temp = positionNumber
        return temp

def reg(username):
    uname = username

    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        #register()
        exit(1)

    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    while ( f.readImage() == False ):
        pass

        ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)
        ## Checks if finger is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber >= 0 ):
        print('Template already exists at position #' + str(positionNumber))
        return 0

    print('Remove finger...')
    time.sleep(0.1)


        ## Wait that finger is read again
    while ( f.readImage() == False ):
        pass

        ## Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(0x02)
        ## Compares the charbuffers
    if ( f.compareCharacteristics() == 0 ):
        raise Exception('Fingers do not match')
        ## Creates a template
    #temp = f.createTemplate()
    ## Creates a template
    f.createTemplate()

    ## Saves template at new position number
    positionNumber = f.storeTemplate()
    temp=[]
    temp=f.downloadCharacteristics(0x01)
    x = []
    x = coll.find_one(sort=[("uid", -1)])
    print(x)
    if x is None:
        new_user = {}
        new_user["uid"] = 0
        new_user["image_template"] = temp
        new_user["username"] = uname
        #new_user = {"uid": next_user, "image_template": last_template, "user_name": uname}
        coll.insert_one(new_user)
    else:
        last_user = x['uid']
        next_user = last_user + 1
        new_user = {}
        new_user["uid"] = next_user
        new_user["image_template"] = temp
        new_user["username"] = uname
        #new_user = {"uid": next_user, "image_template": last_template, "user_name": uname}
        coll.insert_one(new_user)
        
    return 1


def verify_test():
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)

    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    time.sleep(0.1)
    try:
        while ( f.readImage() == False ):
            pass
        f.convertImage(0x01)
        result = f.searchTemplate() ## Searchs template
        positionNumber = result[0]
        accuracyScore = result[1]
        temp = positionNumber
        if ( positionNumber == -1 ):
            print('No match found! Try again')
            time.sleep(0.5)
            #login()
        else:
            print('Found template at position #' + str(positionNumber))
            print('The accuracy score is: ' + str(accuracyScore))
            #return 0
    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)
    
    if ( positionNumber == -1 ):
        print('No match found! Try again....')
        time.sleep(0.5)
        verify_test()
    #else:
    
    return positionNumber
    
def upload_fingerprint_template(name):
    myquery={}
    myquery['username'] = name
    mydoc = coll.find_one(myquery)
    #print(mydoc['uid'])
    print(mydoc['image_template'])
    image_temp = []
    image_temp = mydoc['image_template']
    print(image_temp)
    #image_temp = f.storeTemplate()
    
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)
    result = image_temp
    result = f.searchTemplate()
    positionNumber = result[0]

    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    position = f.getTemplateCount()
    position = position+1
    print("Inserting fingerprint matching user from mongo to local fingerprint sensor")
    f.uploadCharacteristics(0x01, image_temp)
    f.storeTemplate()
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
 
    ####### SUCCESSFULLY UPLOADED CHARACTERISTIC TO LOCAL FP MODULE

def mongo_tests():
    #mydict = {"name": "Stephen"}
    for x in connect_to_collection.find():
        print(x)
    
#upload_fingerprint_template('rindex')
#mongo_tests()
#login() 
