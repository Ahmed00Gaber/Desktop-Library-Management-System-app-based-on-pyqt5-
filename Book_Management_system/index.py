from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUiType #lib for importing floder as it's withoyt conveting to python
import sys
import mysql.connector
import datetime
#responsible for creating excel sheet from data
from xlsxwriter import * 
from xlrd import *
import pyqtgraph as pg


#import folder UI
MainUI,_ = loadUiType('main.ui')


# class book():
#     Add_New_book(self)


#inhert from UI classes
class Main(QMainWindow,MainUI):
    def __init__(self, parent=None):
        super(Main,self).__init__(parent)
        QMainWindow.__init__(self) #overide for design to relate Ui to python code
        self.setupUi(self)

        #connet to db
        self.Db_connect()
        self.Ui_changes() #remove tab bar from UI
        self.Handle_Buttons() #we have to mention every function here

        self.Open_Login_Tab()#if you want program to open on book tap
        self.get_dashboard_data()
        #intialize function that will run directly after project is opened
        self.Show_All_Categories()
        self.Show_Branchies()
        self.Show_Publishers()
        self.Show_Authors()
        self.Show_All_Books()
        self.Show_All_CLients()
        self.Retreive_Day_Work()
        self.Show_emp()

    def Ui_changes(self):
        ##UI changes in login
        self.tabWidget.tabBar().setVisible(False)

    def Db_connect(self):
        ##connection  between app and Db
        self.db=mysql.connector.connect(host='localhost', user='root', password='ahmedgaber011',db='lb')
        self.cur = self.db.cursor() #responsible connecting data between quere and data
        print('connection accepted')

    def Handle_Buttons(self):
        self.pushButton_5.clicked.connect(self.Open_Login_Tab)
        self.pushButton.clicked.connect(self.Open_daily_movment_tap) #opens on daily tap
        self.pushButton_2.clicked.connect(self.Open_Books_Tap)
        self.pushButton_3.clicked.connect(self.Open_CLients_Tap)
        self.pushButton_6.clicked.connect(self.Open_Dashboard_Tap)
        self.pushButton_7.clicked.connect(self.Open_Settings_Tab)

        self.pushButton_39.clicked.connect(self.Add_branch)
        self.pushButton_40.clicked.connect(self.Add_Publisher)
        self.pushButton_41.clicked.connect(self.Add_Author)
        self.pushButton_42.clicked.connect(self.Add_Category)

        self.pushButton_9.clicked.connect(self.Add_Employee)
        self.pushButton_11.clicked.connect(self.Add_New_Book)
        self.pushButton_13.clicked.connect(self.Add_New_Client)

        self.pushButton_27.clicked.connect(self.Edit_Book_search)
        self.pushButton_25.clicked.connect(self.Edit_book)
        self.pushButton_26.clicked.connect(self.Delete_Book)
        self.pushButton_10.clicked.connect(self.All_Books_Filter)
        #export
        self.pushButton_33.clicked.connect(self.Book_export_report)

        self.pushButton_22.clicked.connect(self.Edit_CLient_Search)
        self.pushButton_16.clicked.connect(self.Edit_CLient)
        self.pushButton_17.clicked.connect(self.Delete_Client)
        self.pushButton_35.clicked.connect(self.Client_export_report)
        self.pushButton_12.clicked.connect(self.Client_Filter)

        self.pushButton_8.clicked.connect(self.Handle_Today_work)
        #emp
        self.pushButton_14.clicked.connect(self.check_emp)
        self.pushButton_15.clicked.connect(self.Edit_empolyee_Date) #to save edit to data base  
        #persmissions
        self.pushButton_20.clicked.connect(self.Add_Employee_permission)
        #login
        self.pushButton_80.clicked.connect(self.User_login_permission)

        #dashboard
        self.pushButton_74.clicked.connect(self.get_dashboard_data)
        

    def Handle_login(self):
        pass
    def Handle_reset_pass(self):
        pass

    ###################################### Today
    
    def Handle_Today_work(self):
        ## Handel Day to day operations
        # Get the values for the new row
        book_title = self.lineEdit.text()
        client_nationl_id = self.lineEdit_35.text()
        type = self.comboBox.currentIndex()

        from_date = self.dateEdit_4.date().toPyDate() #it reads default value
        to_date = self.dateEdit_14.date().toPyDate()
        date = datetime.datetime.now()

        branch = 1
        employee = 1

        self.cur.execute("SET FOREIGN_KEY_CHECKS=0") #drop table has fk problem
        # Insert the new row into the table
        self.cur.execute('''
            INSERT INTO daily_movements(book_id , client_id , type,date,branch_id,book_from , book_to , employee_id)
            VALUES(%s , %s , %s , %s , %s , %s , %s , %s)
        ''',(book_title,client_nationl_id,type,date,branch,from_date,to_date,employee))

        # Commit the changes to the database
        self.db.commit()
        self.Retreive_Day_Work()


    def Retreive_Day_Work(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.insertRow(0) #start from row 0
        #wwe are reading from daily movments
        self.cur.execute('''
            SELECT book_id ,type , client_id , book_from , book_to  FROM daily_movements
            ''')
        data = self.cur.fetchall()

        for row , form in enumerate(data):
            for column , item in enumerate(form):
                #this for combo box to check on 1st col if it's 0 or 1 to add rent or retrieve
                if column == 1 : 
                    if item == 0 :
                        self.tableWidget.setItem(row, column, QTableWidgetItem(str("Rent")))
                    else:
                        self.tableWidget.setItem(row , column , QTableWidgetItem(str("Retrieve")))
  
                else:
                    self.tableWidget.setItem(row, column, QTableWidgetItem(str(item)))
                column += 1

            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)

    ############################### Books
    def Show_All_Books(self):
         ## show all clients
        self.tableWidget_3.setRowCount(0)
        self.tableWidget_3.insertRow(0) #insert new row to work on  

        self.cur.execute('''
            SELECT  code,title,category_id, author_id , price from books
        ''')

        data = self.cur.fetchall()
        #enumerate optimize usage of loops it has loop count
        for row , form in enumerate(data): #row= row num data is in form
            for col,item in enumerate(form): # col in each row
                # displaying category name
                
                if col ==2:
                    sql2 = (''' SELECT category_name FROM category WHERE id = %s ''')
                    self.cur.execute(sql2 , [int(item)])
                    category_name = self.cur.fetchone()
                    self.tableWidget_3.setItem(row,col , QTableWidgetItem(str(category_name[0])))

                #for displaying author name
                if col == 3:
                    sql = (''' SELECT name FROM author WHERE id = %s ''')
                    self.cur.execute(sql , [(int(item)+1)]) #this because item=o not present in db
                    author_name = self.cur.fetchone()
                    self.tableWidget_3.setItem(row,col , QTableWidgetItem(str(author_name[0])))
                    
                else:
                    self.tableWidget_3.setItem(row, col, QTableWidgetItem(str(item)))
                col+=1 #to move to the next col

            row_position=self.tableWidget_3.rowCount()
            self.tableWidget_3.insertRow(row_position)  

    #this function to search for book add display them
    def All_Books_Filter(self):
        book_title = self.lineEdit_2.text()
        category = self.comboBox_2.currentIndex() #if ID it's index if text current.text()

        sql = '''
            SELECT code , title , category_id , author_id , publisher_id FROM books WHERE title = %s 
        '''
        self.cur.execute(sql ,[(book_title)])
        data = self.cur.fetchall()
        self.tableWidget_3.setRowCount(0)
        self.tableWidget_3.insertRow(0) #insert new row to work on
        for row , form in enumerate(data): #row= row num data is in form
            for col,item in enumerate(form): # col in each row
                self.tableWidget_3.setItem(row,col,QTableWidgetItem(str(item)))
                col+=1 #to move to the next col

            row_position=self.tableWidget_3.rowCount()
            self.tableWidget_3.insertRow(row_position)  

        if book_title=="":
            self.Show_All_Books()   

    def Add_New_Book(self):
        ## add new book
        book_title = self.lineEdit_3.text()
        category = self.comboBox_4.currentIndex()
        description = self.textEdit.toPlainText()
        price = self.lineEdit_4.text()
        code = self.lineEdit_6.text()
        publisher = self.comboBox_7.currentIndex()
        author = self.comboBox_6.currentIndex()
        status = self.comboBox_5.currentIndex()
        part_order = self.lineEdit_5.text()
        barcode = self.lineEdit_15.text()
        date = datetime.datetime.now()

        self.cur.execute('''
            INSERT INTO books(title,description,category_id,code,barcode,part_order,price,author_id ,publisher_id,status,date)
            VALUES (%s , %s , %s , %s,%s , %s , %s , %s , %s , %s  , %s)
        ''',(book_title,description,category,code,barcode,part_order,price,author ,publisher,status , date))

        self.db.commit()
        self.Show_All_Books()
        self.statusBar().showMessage('Book added successfully   ')

        #clear
        self.lineEdit_3.setText('') #title
        self.lineEdit_4.setText('')#price
        self.lineEdit_6.setText('')#code
        self.lineEdit_5.setText('')#part order
        self.lineEdit_15.setText('')#bar code
        self.textEdit.clear()#description

    def Edit_Book_search(self):
        book_code =self.lineEdit_31.text() #read from input line

        sql= (''' 
            SELECT * from books where code=%s 
        ''')
        self.cur.execute(sql,[(book_code)])    

        data= self.cur.fetchone()
        
        self.lineEdit_38.setText(data[1]) #title
        self.textEdit_3.setPlainText(data[2]) #plain text
        self.lineEdit_41.setText(data[3])#code
        self.comboBox_18.setCurrentIndex(int(data[10])) #category
        self.lineEdit_40.setText(str(data[6]))#price
        self.comboBox_20.setCurrentIndex(int(data[11]))#publisher
        self.comboBox_17.setCurrentIndex(int(data[12]))#author
        self.comboBox_19.setCurrentIndex(int(data[8]))#status
        self.lineEdit_39.setText(str(data[5]))#part order
        
    #save changes done    
    def Edit_book(self):
        book_title = self.lineEdit_38.text()
        category = self.comboBox_18.currentIndex()
        description = self.textEdit_3.toPlainText()
        price = self.lineEdit_40.text()
        code = self.lineEdit_41.text()
        publisher = self.comboBox_20.currentIndex()
        author = self.comboBox_17.currentIndex()
        status = self.comboBox_19.currentIndex()
        part_order = self.lineEdit_39.text()
        
        self.cur.execute('''
            UPDATE books SET title=%s ,description=%s ,code = %s ,part_order = %s , price = %s , status = %s , category_id=%s,publisher_id=%s,author_id=%s WHERE code = %s   
        ''',(book_title,description,code,part_order,price,status,category,publisher,author,code))

        self.db.commit()
        self.Show_All_Books()

        #modify message to the status bar or as a message box
        self.statusBar().showMessage('Book has been modified')
        #should take 3 arguments
        QMessageBox.information(self,"sucess","Book has been modified")

        self.lineEdit_38.setText('') #title
        self.lineEdit_40.setText('')#price
        self.lineEdit_41.setText('')#code
        self.lineEdit_39.setText('')#part order
        self.lineEdit_31.setText('')#entry code
        self.textEdit_3.clear()#description

    def Delete_Book(self):
        ## delete client from DB
        book_code = self.lineEdit_31.text()

        delete_message = QMessageBox.warning(self ,"Delete" , " Are you sure you want to delete Book ",QMessageBox.Yes | QMessageBox.No )
        if delete_message == QMessageBox.Yes :
            sql = ('''
                DELETE FROM books WHERE code = %s
            ''' )

            self.cur.execute(sql , [(book_code)])

            self.db.commit()
            self.statusBar().showMessage('Book has been deleted Succefuly ')
            self.Show_All_Books()

            self.lineEdit_38.setText('') #title
            self.lineEdit_40.setText('')#price
            self.lineEdit_41.setText('')#code
            self.lineEdit_39.setText('')#part order
            self.lineEdit_31.setText('')#entry code
            self.textEdit_3.clear()#description


    ############################### Client ################
     ###########################################
    def Show_All_CLients(self):
        ## show all clients
        self.tableWidget_4.setRowCount(0)
        self.tableWidget_4.insertRow(0)

        self.cur.execute('''
            SELECT name , mail , phone , national_id , date FROM clients
        ''')

        data = self.cur.fetchall()

            ## row = iteration , form = data
        for row , form in enumerate(data):
            for col , item in enumerate(form):
                self.tableWidget_4.setItem(row,col , QTableWidgetItem(str(item)))
                col += 1

            row_position = self.tableWidget_4.rowCount()
            self.tableWidget_4.insertRow(row_position)


    def Add_New_Client(self):
        ## add new Client
        client_name = self.lineEdit_38.text() #title
        client_email = self.lineEdit_40.text() #price
        client_phone = self.lineEdit_11.text()
        client_national_id = self.lineEdit_12.text()
        date = datetime.datetime.now()

        self.cur.execute('''
            INSERT INTO clients(name,mail,phone,national_id,date)
            VALUES (%s , %s , %s ,%s , %s)
        ''' , (client_name , client_email , client_phone , client_national_id , date))

        
        self.db.commit()
        self.Show_All_CLients()
        self.statusBar().showMessage('client added successfully   ')

    #function display client in table like books for search zzzxxxxx
    def Client_Filter(self):
        client_name = self.lineEdit_7.text()

        sql = '''
            SELECT name,mail,phone,national_id,date FROM clients WHERE name = %s 
        '''
        self.cur.execute(sql ,[(client_name)])
        data = self.cur.fetchall()
        #clear widget before add
        self.tableWidget_4.setRowCount(0)
        self.tableWidget_4.insertRow(0) #insert new row to work on
        for row , form in enumerate(data): #row= row num data is in form
            for col,item in enumerate(form): # col in each row
                self.tableWidget_4.setItem(row,col,QTableWidgetItem(str(item)))
                col+=1 #to move to the next col

            row_position=self.tableWidget_3.rowCount()
            self.tableWidget_4.insertRow(row_position)
        
        if client_name=="":
            self.Show_All_CLients()

    def Edit_CLient_Search(self):
        ## edit client
        client_data = self.lineEdit_30.text()

        if self.comboBox_11.currentIndex() == 0 :
            sql = ('''SELECT * FROM clients WHERE name = %s''')
            self.cur.execute(sql , [(client_data)])
            data = self.cur.fetchone()


        if self.comboBox_11.currentIndex() == 1 :
            sql = ('''SELECT * FROM clients WHERE mail = %s''')
            self.cur.execute(sql , [(client_data)])
            data = self.cur.fetchone()



        if self.comboBox_11.currentIndex() == 2 :
            sql = ('''SELECT * FROM clients WHERE phone = %s''')
            self.cur.execute(sql , [(client_data)])
            data = self.cur.fetchone()



        if self.comboBox_11.currentIndex() == 3 :
            sql = ('''SELECT * FROM clients WHERE national_id = %s''')
            self.cur.execute(sql , [(client_data)])
            data = self.cur.fetchone()


        #write the values came from db
        self.lineEdit_17.setText(data[1]) #name
        self.lineEdit_20.setText(data[2]) # email
        self.lineEdit_19.setText(data[3]) #phone
        self.lineEdit_18.setText(str(data[5])) #NID


    def Edit_CLient(self):
        ## edit client
        client_name = self.lineEdit_17.text()
        client_mail = self.lineEdit_20.text()
        client_phone = self.lineEdit_19.text()
        client_national_id = self.lineEdit_18.text()


        self.cur.execute('''
            UPDATE clients SET name = %s , mail = %s , phone = %s , national_id = %s where name= %s
        ''' , (client_name,client_mail,client_phone,client_national_id,client_name))


        self.db.commit()
        self.statusBar().showMessage('client modified successfully')
        self.Show_All_CLients()

        self.lineEdit_17.setText('') #name
        self.lineEdit_20.setText('')#mail
        self.lineEdit_19.setText('')#phone
        self.lineEdit_18.setText('')#NID
        
    #delete only on name
    def Delete_Client(self):
        ## delete client from DB
        client_name = self.lineEdit_17.text()
        delete_message = QMessageBox.warning(self ,"مسح معلومات" , "هل انت متاكد من مسح العميل",QMessageBox.Yes | QMessageBox.No )

        if delete_message == QMessageBox.Yes :

            sql = ('''DELETE FROM clients WHERE name = %s''')
            self.cur.execute(sql , [(client_name)])
        
            self.db.commit()
            self.statusBar().showMessage('Client deleted successfully ')
            self.Show_All_CLients()

            self.lineEdit_17.setText('') #name
            self.lineEdit_20.setText('')#mail
            self.lineEdit_19.setText('')#phone
            self.lineEdit_18.setText('')#NID
            self.lineEdit_30.setText('')#entry data

    ############################### History    
    def Show_History(self):
        pass
    ############################### Report
    ##Books reprot    
    def All_Books_report(self):
        pass
    def Books_filter_report(self):
        pass    
    def show_Book_report(self):
        pass

    def Book_export_report(self):
        #export Data to excel file

        self.cur.execute('''
            SELECT  code,title,category_id, author_id , price from books
        ''')
        data = self.cur.fetchall()
        excel_sheet=Workbook("book_report.xlsx")
        sheet1=excel_sheet.add_worksheet()#add at the first page data
        sheet1.write(0,0,'Book_code')
        sheet1.write(0,1,'Book_title')
        sheet1.write(0,2,'category')
        sheet1.write(0,3,'author')
        sheet1.write(0,4,'price')

        row_num=1
        for row in data:
            col_num=0
            for item in row:
                sheet1.write(row_num,col_num,str(item))
                col_num+=1
            row_num+=1
        excel_sheet.close()
        self.statusBar().showMessage('Book file expoerted succefuly ')

    ##Client reprot    
    def All_Client_report(self):
        pass

    def Client_filter_report(self):
        pass    
    def show_Client_report(self):
        pass
    def Client_export_report(self):

        self.cur.execute('''
            SELECT name , mail , phone , national_id  FROM clients
        ''')
        data = self.cur.fetchall()
        file_sheet=Workbook("Client_report.xlsx")
        sheet1=file_sheet.add_worksheet()#add at the first page data
        sheet1.write(0,0,'name')
        sheet1.write(0,1,'mail')
        sheet1.write(0,2,'phone')
        sheet1.write(0,3,'national_id')
       

        row_num=1
        for row in data:
            col_num=0
            for item in row:
                sheet1.write(row_num,col_num,str(item))
                col_num+=1
            row_num+=1
        file_sheet.close()
        self.statusBar().showMessage('client file expoerted succefuly ')

    ### Monthly Report
    def Monthly_report(self):
        pass
    def Monthly_report_export(self):
        #export monthly report
        pass

    ############################### Settings TAP ##############################
    def Add_branch(self):
        branch_name = self.lineEdit_64.text() #read text written save then send branch name
        branch_code = self.lineEdit_65.text()
        branch_location = self.lineEdit_66.text()

        self.cur.execute(''' 
            INSERT INTO branch(name , code , location)
            VALUES (%s , %s , %s)
            ''', (branch_name , branch_code,branch_location))
        self.db.commit() #db without saved on comp ram but when used saved to db
        self.lineEdit_64.setText('')#
        self.lineEdit_65.setText('')#
        self.lineEdit_66.setText('')#
        self.Show_Branchies()

    def Add_Category(self):
        Category_name= self.lineEdit_71.text()
        parent_category_text = self.comboBox_15.currentText() #choosen from user

        #make parent category related to id 
        query = ''' SELECT id FROM category where Category_name = %s'''
        self.cur.execute(query,[(parent_category_text)])
        
        data = self.cur.fetchone()#only 1 value
        parent_category= data[0] #use it's ID

        self.cur.execute('''
            INSERT INTO category (Category_name,parent_category)
            VALUES (%s , %s)
        ''',(Category_name,parent_category))
        self.db.commit()
        self.lineEdit_71.setText('')#
        self.statusBar().showMessage(' Category added ')
        self.Show_All_Categories()

    def Add_Publisher(self):
        ## add new publisher
        publisher_name = self.lineEdit_67.text()
        publisher_location = self.lineEdit_68.text()

        self.cur.execute('''
                INSERT INTO publisher(name , location)
                VALUES (%s , %s)
            ''' , (publisher_name , publisher_location))
        self.db.commit()
        self.lineEdit_67.setText('')#
        self.lineEdit_68.setText('')#
        self.statusBar().showMessage(' Publisher added')
        self.Show_Publishers()

    def Add_Author(self):
         ## add new author
        author_name = self.lineEdit_69.text()
        author_location = self.lineEdit_70.text()

        self.cur.execute(''' 
                INSERT INTO author(name , location)
                VALUES (%s , %s)
            ''' , (author_name , author_location))

        self.db.commit()
        self.lineEdit_69.setText('')#
        self.lineEdit_70.setText('')#
        self.statusBar().showMessage(' Author added ')
        self.Show_Authors()
    ######### functions to help category ############
    ##################################### show functions
    def Show_All_Categories(self):
        self.comboBox_15.clear()
        self.cur.execute('''
            SELECT category_name FROM category
        ''')
        categories =self.cur.fetchall()

        for category in categories :
            self.comboBox_15.addItem(str(category[0]))
            self.comboBox_4.addItem(str(category[0]))
            self.comboBox_18.addItem(str(category[0]))

    def Show_Branchies(self):
        self.cur.execute('''
            SELECT name FROM branch
        ''')
        branchies =self.cur.fetchall()
        for branch in branchies:
            self.comboBox_21.addItem(branch[0])
            self.comboBox_22.addItem(branch[0])

    def Show_Publishers(self):
        self.cur.execute('''
            SELECT name FROM publisher
        ''')
        publishers = self.cur.fetchall()
        for publisher in publishers:
            self.comboBox_7.addItem(publisher[0])
            self.comboBox_20.addItem(publisher[0])

    def Show_Authors(self):
        self.cur.execute(''' 
            SELECT name FROM author
        ''')
        authors = self.cur.fetchall()
        for author in authors :
            self.comboBox_17.addItem(author[0])
            self.comboBox_6.addItem(author[0])


    def Show_emp(self):
        self.cur.execute('''
            SELECT * FROM employee
        ''')
        #put empolyee data as tuple of tuple into data
        data = self.cur.fetchall() 
        for emp in data:
            self.comboBox_16.addItem(emp[1]) # slising for emp

    ###############################
    def Add_Employee(self):
        ## add new employee
        employee_name = self.lineEdit_8.text()
        employee_email = self.lineEdit_13.text()
        employee_phone = self.lineEdit_16.text()
        employee_branch_ = self.comboBox_21.currentIndex()
        national_id = self.lineEdit_21.text()
        periority = self.lineEdit_33.text()
        password = self.lineEdit_22.text()
        password2 = self.lineEdit_23.text()
        date = datetime.datetime.now()
        
        if password == password2 :

            self.cur.execute('''
                INSERT INTO employee (name , mail , phone , branch , national_id ,date, periority , password)
                VALUES (%s , %s , %s , %s , %s , %s , %s , %s)
            ''' , (employee_name,employee_email,employee_phone,employee_branch_,national_id,date,periority , password))

            self.db.commit()
            #cleat after finishing
            self.lineEdit_8.setText('') #name
            self.lineEdit_13.setText('')#email
            self.lineEdit_16.setText('')#phone
            self.lineEdit_21.setText('')#nationalID
            self.lineEdit_33.setText('') #priority
            self.lineEdit_22.setText('') #pass
            self.lineEdit_23.setText('')#confrim pass
            self.statusBar().showMessage('client added successfully   ')
        else:
            print('wrong password')

    def check_emp(self):
        employee_name=self.lineEdit_24.text()
        password=self.lineEdit_25.text()

        self.cur.execute(""" SELECT * FROM employee""")
        data =   self.cur.fetchall()

        for row in data:
            if row[1] ==employee_name and row[7]==password:
                self.groupBox_7.setEnabled(True)

                self.lineEdit_29.setText(row[2]) #email
                self.lineEdit_26.setText(row[3]) #phone
                self.comboBox_22.setCurrentIndex(row[8]) #location
                self.lineEdit_27.setText(str(row[5])) #national ID
                self.lineEdit_28.setText(row[7]) #password
                self.lineEdit_34.setText(str(row[6])) #priority

    def Edit_empolyee_Date(self):
        #take data from entry
        employee_name = self.lineEdit_24.text()
        employee_email = self.lineEdit_29.text()
        employee_phone = self.lineEdit_26.text()
        employee_branch_ = self.comboBox_22.currentIndex()
        national_id = self.lineEdit_27.text()
        periority = self.lineEdit_34.text()
        password = self.lineEdit_28.text()

        #update on db
        self.cur.execute('''
            UPDATE employee SET mail=%s ,phone = %s , Branch = %s , national_id = %s ,Periority=%s,password=%s WHERE name=%s
        ''',(employee_email,employee_phone,employee_branch_,national_id,periority,password,employee_name))

        self.db.commit()
        self.statusBar().showMessage('Empolyee data has been modified successfully ')

        #clear screen
        self.lineEdit_24.setText('') #name
        self.lineEdit_29.setText('')#email
        self.lineEdit_26.setText('')#phone
        self.lineEdit_27.setText('')#nationalID
        self.lineEdit_34.setText('') #priority
        self.lineEdit_28.setText('') #pass
        self.lineEdit_25.setText('') #pass

        #set enable to false after finishing
        self.groupBox_7.setEnabled(False)
    ###############################

    def Add_Employee_permission(self):
        empolyee_name = self.comboBox_16.currentText()

        books_tab = 0
        clients_tab = 0
        dashboard_tab = 0
        history_tab = 0
        reports_tab = 0
        settings_tab = 0

        add_book = 0
        edit_book = 0
        delete_book = 0
        import_book = 0
        export_book = 0

        add_client = 0
        edit_client = 0
        delete_client = 0
        import_client = 0
        export_client = 0


        add_branch = 0
        add_publisher = 0
        add_author= 0
        add_category = 0
        add_employee = 0
        edit_employee = 0

        #admin check
        if self.checkBox_32.isChecked() == True:
            self.cur.execute('''
                INSERT INTO empolyee_permissions (empolyee_name,books_tab,clients_tab,dashboard_tab,history_tab,reports_tab,settings_tab,
                    add_book,edit_book,delete_book,import_book,export_book  ,
                    add_client,edit_client,delete_client,import_client,export_client ,
                    add_branch,add_publisher,add_author,add_category,add_employee,edit_employee)
                 VALUES(%s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s, %s , %s , %s , %s , %s, %s , %s , %s , %s , %s , %s)
            ''' , ( empolyee_name, 1 ,1 ,  1 , 1 ,1 , 1, 1 , 1 , 1 , 1 , 1 ,1 , 1 , 1 , 1 , 1 ,1 , 1 , 1 , 1 , 1 , 1))

            self.db.commit()
            self.statusBar().showMessage('All permissions added successfully')
        
        else:
            ### TAPS
            if self.checkBox_8.isChecked() == True:
                books_tab = 1

            if self.checkBox_9.isChecked() == True:
                clients_tab = 1

            if self.checkBox_7.isChecked() == True:
                dashboard_tab = 1

            if self.checkBox_10.isChecked() == True:
                settings_tab = 1

            ### books
            if self.checkBox.isChecked() == True :
                add_book = 1

            if self.checkBox_2.isChecked() == True :
                edit_book = 1

            if self.checkBox_3.isChecked() == True :
                delete_book = 1

            if self.checkBox_14.isChecked() == True :
                import_book = 1

            if self.checkBox_15.isChecked() == True :
                export_book = 1


                ### clients
            if self.checkBox_4.isChecked() == True :
                add_client = 1

            if self.checkBox_5.isChecked() == True :
                edit_client = 1

            if self.checkBox_6.isChecked() == True :
                delete_client = 1

            if self.checkBox_16.isChecked() == True :
                import_client = 1

            if self.checkBox_17.isChecked() == True :
                export_client = 1



                ### settings
            if self.checkBox_28.isChecked() == True :
                add_branch = 1

            if self.checkBox_29.isChecked() == True :
                add_publisher = 1

            if self.checkBox_27.isChecked() == True :
                add_author = 1

            if self.checkBox_30.isChecked() == True :
                add_category = 1

            if self.checkBox_33.isChecked() == True :
                add_employee = 1

            if self.checkBox_31.isChecked() == True :
                edit_employee = 1
            
            #this line is that there was problem in emp_permissions i add primary key each time  
            # self.cur.execute('''ALTER TABLE empolyee_permissions ADD idempolyee_permissions INT AUTO_INCREMENT PRIMARY KEY FIRST''')
            
            self.cur.execute('''
                    INSERT INTO empolyee_permissions (empolyee_name,books_tab,clients_tab,dashboard_tab,history_tab,reports_tab,settings_tab,
                        add_book,edit_book,delete_book,import_book,export_book  ,
                        add_client,edit_client,delete_client,import_client,export_client ,
                        add_branch,add_publisher,add_author,add_category,add_employee,edit_employee)
                    VALUES(%s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s, %s , %s , %s , %s , %s, %s , %s , %s , %s , %s , %s)
                ''' , ( empolyee_name, books_tab ,clients_tab ,  dashboard_tab , history_tab ,reports_tab , settings_tab
                        , add_book , edit_book , delete_book , import_book , export_book ,
                        add_client , edit_client , delete_client , import_client , export_client ,
                        add_branch , add_publisher , add_author , add_category , add_employee , edit_employee))

            self.db.commit()
            self.statusBar().showMessage('premissions added successfully')


    def admin_report():
        #send report to the admins
        pass

    ######################### TAPS #########################
    #connect taps with buttons 
    def Open_Login_Tab(self):
        self.tabWidget.setCurrentIndex(0)

    def Open_Reset_Password_Tab(self):
        self.tabWidget.setCurrentIndex(1)

    def Open_daily_movment_tap(self):
        self.tabWidget.setCurrentIndex(2)#count start from 0

    def Open_Books_Tap(self):
        self.tabWidget.setCurrentIndex(3)
        self.tabWidget_2.setCurrentIndex(0)

    def Open_CLients_Tap(self):
        self.tabWidget.setCurrentIndex(4)
        self.tabWidget_3.setCurrentIndex(0)

    def Open_Dashboard_Tap(self):
        self.get_dashboard_data() #if any kind of updates happen on the sytem in updates 
        self.tabWidget.setCurrentIndex(5)

    def Open_History_Tap(self):
        self.tabWidget.setCurrentIndex(6)

    def Open_Report_Tap(self):
        self.tabWidget.setCurrentIndex(7)
        self.tabWidget_5.setCurrentIndex(0)#when open it will open on first page

    def Open_Settings_Tab(self):
        self.tabWidget.setCurrentIndex(8)    
        self.tabWidget_4.setCurrentIndex(0) 

########################################### login #########################
    def User_login_permission(self):
        username =self.lineEdit_100.text()
        password =self.lineEdit_99.text()

        self.cur.execute(""" SELECT name , password FROM employee""")
        data = self.cur.fetchall()

        for row in data:
            if row[0] ==username and row[1]==password:
                self.groupBox_9.setEnabled(True)   
                self.pushButton.setEnabled(True) #today tab
                self.pushButton_5.setEnabled(True)
                self.statusBar().showMessage(' Correct user name and password')
                # QMessageBox.information(self,'correct'," logged_in")

                self.cur.execute('''
                    SELECT * from empolyee_permissions where empolyee_name= %s
                ''',(username,))
                data_permissions=self.cur.fetchone()

                if data_permissions[2]== 1: #book tab
                    self.pushButton_2.setEnabled(True)  
                elif data_permissions[2]== 0: #book tab
                    self.pushButton_2.setEnabled(False)  

                if data_permissions[3]== 1: #client tab
                    self.pushButton_3.setEnabled(True)
                elif data_permissions[3]== 0: #book tab
                    self.pushButton_3.setEnabled(False) 

                if data_permissions[4]== 1: #Dashbard tab
                    self.pushButton_6.setEnabled(True)
                elif data_permissions[4]== 0: #book tab
                    self.pushButton_6.setEnabled(False) 

                if data_permissions[7]== 1: #settings tab
                    self.pushButton_7.setEnabled(True)

                elif data_permissions[7]== 0: #book tab
                    self.pushButton_7.setEnabled(False) 


                if data_permissions[8]== 1: # add book 
                    self.pushButton_11.setEnabled(True)  

                if data_permissions[9]== 1: #edit book
                    self.pushButton_25.setEnabled(True)

                if data_permissions[10]== 1: #delete book
                    self.pushButton_26.setEnabled(True)

                # if data_permissions[11]== 1: #import book
                #     self.pushButton_34.setEnabled(True)


                if data_permissions[12]== 1: # add client 
                    self.pushButton_13.setEnabled(True)  

                if data_permissions[13]== 1: #edit client
                    self.pushButton_16.setEnabled(True)

                if data_permissions[14]== 1: #delete client
                    self.pushButton_17.setEnabled(True)

                # if data_permissions[15  ]== 1: #import client
                #     self.pushButton_36.setEnabled(True)
                

                if data_permissions[16]== 1: # add branch 
                    self.pushButton_39.setEnabled(True)  

                if data_permissions[17]== 1: #add author 
                    self.pushButton_41.setEnabled(True)

                if data_permissions[18]== 1: #add empolyee 
                    self.pushButton_9.setEnabled(True)

                if data_permissions[19  ]== 1: #edit empolyee
                    self.pushButton_15.setEnabled(True)


                if data_permissions[20  ]== 1: #export book
                    self.pushButton_33.setEnabled(True)

                if data_permissions[21  ]== 1: #export client
                    self.pushButton_35.setEnabled(True)

                if data_permissions[22  ]== 1: #add publisher
                    self.pushButton_40.setEnabled(True)

                if data_permissions[23  ]== 1: #add category
                    self.pushButton_42.setEnabled(True)


    ########################## Dashboard ###################
    def get_dashboard_data(self):
        ## retrieve data
        ## retrieve data
        filter_date = self.dateEdit_13.date() #read date
        filter_date = filter_date.toPyDate() #conver to redable format
        year = str(filter_date).split('-')[0] #to find year data
        
        self.cur.execute(""" 
            SELECT COUNT(book_id), EXTRACT(MONTH FROM Book_from) as month
            FROM daily_movements
            WHERE year(Book_from) = %s
            GROUP BY month
        """ %(year))

        pen = pg.mkPen(color=(255,0,0))
        data = self.cur.fetchall()

        #we should pass array so we wait till it full then pass our data
        books_count = []
        rent_count = []
        for row in data:
                books_count.append(row[0])
                rent_count.append(row[1])

        

        barchart = pg.BarGraphItem(x=rent_count , height=books_count , width=.2)
        #update graph with user
        for item in self.widget.items():
            if isinstance(item, pg.BarGraphItem):
                self.widget.removeItem(item)

        self.widget.addItem(barchart) #change type of displaying to barchart
        self.widget.setTitle('Sales') # size , color 
        self.widget.addLegend()
        self.widget.setLabel('left' ,'no of rented books' , color='red' , size=40 )
        self.widget.setLabel('bottom' ,' Month' , color='red' , size=40 )
        self.widget.showGrid(x=True,y=True)

def main(): 
    app=QApplication(sys.argv)
    window = Main() #object from class
    window.show()
    #main loop
    app.exec_()

#run code from main function
if __name__ == '__main__':
    main()