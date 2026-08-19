#HERE WE WILL USE CONDITION LOOP AND DICTIONARY
#INN THIS TEACHER CAN ADD STUDENTS ,VIEW ALL STUDENTS ,CHECK RESULKTS AND EXIT
student={}
while True:
    print("-------------------------------------")
    print("STUDENTS MANAGER APP")
    print("-------------------------------------")
    print("[1] Add Students")
    print("[2] View Students")
    print("[3] Check Result")
    print("[4]  Exit")
    choice = input("Enter your choice:")
    #add students
    if choice =="1":
        name=input("Enter students name:")
        marks = int(input("enter marks:"))
        student[name] = marks
        print(f"{name}Succeefully Added!")

        #view studentds 
    elif choice == "2":
        if not student:
            print("No Student found!")
        else:
            for name, marks in student.items():    
                print(name, ":", marks)

        #check result
    elif choice == "3":
        name= input("enter student name:")

        if name in student:
            marks = student[name]
            if marks >=40:
                print ("PASS")
            else:
                print("FAIL")
        else:
            print("student Not found!")

    #exit
    elif choice =="4":
          print("Exiting....")       
          break
    else:
        print("In-valid input")

