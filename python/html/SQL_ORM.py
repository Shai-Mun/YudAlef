import sqlite3

import pickle
    # https://docs.python.org/2/library/sqlite3.html
    # https://www.youtube.com/watch?v=U7nfe4adDw8


__author__ = 'Yossi'

from math import floor


class Apartment(object):
    def __init__(self,owner,aprt_pass,street,flr,num,email,phone,accountID,isAdmin):
        self.owner = owner
        self.aprt_pass = aprt_pass
        self.street = street
        self.floor = flr
        self.num = num
        self.email = email
        self.phone = phone
        self.account_ID = accountID
        self.isAdmin = isAdmin

    def new_pass(self,new_pass):
        self.aprt_pass= new_pass

    def change_manager_status(self):
        self.is_manager = not self.is_manager

    def __str__(self):
        return "user:"+self.owner+ ":"+self.aprt_pass+ ":"+self.street+ ":" + \
                      self.floor+":"+self.num+ ":"+self.phone+ ":"+self.email+ ":"+ \
                      str(self.account_ID)+":"+self.isAdmin

class Landlord(object):
    def __init__(self,acc_id,balance,manager,):
        self.id=acc_id
        self.balance=balance
        self.manager=manager
        self.credit_cards=[]





    
class UserAccountORM():
    def __init__(self):
        self.conn = None  # will store the DB connection
        self.cursor = None   # will store the DB connection cursor

    def open_db(self):
        """
        will open DB file and put value in:
        self.conn (need DB file name)
        and self.cursor
        """
        self.conn = sqlite3.connect('UserAccount.db')
        self.current = self.conn.cursor()
        
        
    def close_db(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()




    #All read SQL

    def get_user(self, username):
        self.open_db()

        usr=None
        sql= "SELECT ................ "
        res= self.current.execute(sql)




         
        self.close_db()
        return usr
    
    def get_accounts(self):
        pass

    def get_users(self):
        self.open_db()
        usrs=[]






        self.close_db()

        return usrs



    def get_user_balance(self,username):
        self.open_db()

        sql="SELECT a.Balance FROM Accounts a , Users b WHERE a.Accountid=b.Accountid and b.Username='"+username+"'"
        res = self.current.execute(sql)
        for ans in res:
            balance =  ans[0]
        self.close_db()
        return balance


    #__________________________________________________________________________________________________________________
    #__________________________________________________________________________________________________________________
    #______end of read start write ____________________________________________________________________________________
    #__________________________________________________________________________________________________________________
    #__________________________________________________________________________________________________________________
    #__________________________________________________________________________________________________________________




    #All write SQL


    def withdraw_by_username(self,amount,username):
        """
        return true for success and false if failed
        """
        pass
        

    def deposit_by_username(self,amount,username):
         pass




    def insert_new_user(self,username,password,firstname,lastname,address,phone,email,acid):
         pass

    
    #def insert_new_account(self,username,password,firstname,lastname,address,phone,email):
    def insert_new_account(self,user):
        self.open_db()
        sql= "SELECT MAX(Accountid) FROM Accounts"
        res = self.current.execute(sql)
        for ans in res:
            accountID= ans[0]+1
        sql="INSERT INTO Users (Username, Password, Fname, Lname, Adress, Phone, Email,Accountid,Isadmin)"
        sql+=" VALUES('"+user.username+"','"+user.password+"','"+user.firstname+"','"+user.lastname+"',"
        sql+="'" + user.street + "','" + user.phone + "','" + user.email + "'," + str(accountID) + ",'no')"
        res =self.current.execute(sql)
        sql="INSERT INTO Accounts (Accountid,Balance,Manager) VALUES("+str(accountID)+",0,'"+user.username+"')"
        res=self.current.execute(sql)
        self.commit()
        self.close_db()
        print (res)
        return "Ok"


    def update_user(self,user):
        self.open_db()



        self.close_db()
        return True


    def update_account(self,account):
        pass



    def delete_user(self,username):
        pass

    def delete_account(self,accountID):
        pass


def main_test():
    user1= Apartment("Yos", "12345", "yossi", "zahav", "kefar saba", "123123123", "1111", 1, '11')

    db= UserAccountORM()
    db.delete_user(user1.owner)
    users= db.get_users()
    for u in users :
        print(u)

if __name__ == "__main__":
    main_test()


