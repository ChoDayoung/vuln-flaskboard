
#-*- coding: utf-8 -*-
from flask import Flask,render_template,request,session,redirect,url_for,send_from_directory
import pymysql,sys,re
import hashlib
import datetime
from werkzeug import secure_filename
reload(sys)
sys.setdefaultencoding('utf-8')

app=Flask(__name__)
app.secret_key='a'

host='localhost'
data_base='boarddb'
user='root'
password='123456'


def get_db():
    db=pymysql.connect(host=host,user=user,passwd=password,db=data_base)
    return db

"""def init_db():
    db=get_db()
    sql_member=CREATE table member(user_num int(10) PRIMARY KEY, user_id varchar(30) not null, user_pass varchar(50) not null, user_nik varchar(50) UNIQUE, user_mail varchar(80) not null, user_phone int(80) not null);
    db.execute(sql_member)
    db.commit()
    
    sql_board=CREATE table board(bbs_no int(10) PRIMARY KEY, bbs_title varchar(50) not null, bbs_content varchar(500) not null, bbs_writer varchar(20) not null,bbs_date varchar(20) not null , bbs_pass varchar(20), bbs_file varchar(200));
    db.execute(sql_board)
    db.commit()"""

def add_account(userid_add,userps_add,usernick_add,email,phone):
    db=get_db()
    userps_add=hashlib.sha224(userps_add).hexdigest()
    sql="INSERT INTO member(user_id, user_pass, user_nik, user_mail, user_phone) VALUES('%s','%s','%s','%s',%d)" %(userid_add,userps_add,usernick_add,email,int(phone))
    conn=db.cursor()
    conn.execute(sql)
    db.commit()

@app.route('/add_user',methods=['GET','POST'])
def add_account_form():
    if request.method=='GET':
        return render_template('add_user.html')
    else:
        userid_add=request.form.get('userid_add')
        userps_add=request.form.get('userps_add')
        usernick_add=request.form.get('usernick_add')
        email=request.form.get('email')
        phone=request.form.get('phone')
        """if len(dup_r)==0:"""
        add_account(userid_add=request.form['userid_add'],userps_add=request.form['userps_add'],usernick_add=request.form['usernick_add'],email=request.form['email'], phone=request.form['phone'])
        """elif len(dup_r)!=0:
            return ''' <script language=javascript>
		    alert('중복된 ID가 있습니다!!')
		    location.href=history.back(); 
                    </script>'''"""
        return redirect(url_for('login'))


		
def get_account(userid,userps):
    db=get_db()
    userps=hashlib.sha224(userps).hexdigest()
    sql="SELECT * FROM member where user_id='%s' and user_pass='%s'" %(userid,userps)
    conn=db.cursor()
    conn.execute(sql)
    r_ser=conn.fetchall()
    return r_ser


def add_board(board_title,board_write,filename,bbs_pass):
    db=get_db()
    day=datetime.datetime.today().strftime("%Y-%m-%d %H:%M")
    data=(board_title,board_write,session['nickname'],day,bbs_pass,filename)
    sql="INSERT INTO board(bbs_title,bbs_content,bbs_writer,bbs_date,bbs_pass,bbs_file) VALUES(%s,%s,%s,%s,%s,%s)" 
    conn=db.cursor()
    conn.execute(sql,data)
    db.commit()


@app.route('/add_write',methods=['GET','POST'])
def add_board_form():
    if request.method=='GET':
        if 'userid' not in session:
            return redirect(url_for('login'))
        return render_template('add_write.html')
    else:
        board_title=request.form.get('board_title') 
        board_write=request.form.get('board_write')     
	try:
            f=request.files['_file']
            f.save('./uploads/'+secure_filename(f.filename))
        except:
	    pass
	
        if len(board_title)==0 or len(board_write)==0:
	    return ''' <script language=javascript>
		    alert('값을 입력해주세요!!')
		    location.href=history.back(); 
	 	    </script>'''
        else:
            add_board(board_title=request.form['board_title'],board_write=request.form['board_write'],filename=f.filename,bbs_pass=None)
        return redirect(url_for('board_main'))

def get_board():
    db=get_db()
    sql="select * from board;"
    conn=db.cursor()
    conn.execute(sql)
    r_ser=conn.fetchall()
    return r_ser

def del_board_db(bbs_no):
    db=get_db()
    sql="delete from board where bbs_no=%s"
    conn=db.cursor()
    conn.execute(sql,bbs_no)
    db.commit()

def chk_db(bbs_no):
    db=get_db()
    sql="select * from board where bbs_no=%s"
    conn=db.cursor()
    conn.execute(sql,bbs_no)
    r_ser=conn.fetchall()
    return r_ser

@app.route('/board_view/delete')
def del_board_view():
    bbs_no=request.args.get('bbs_no')
    del_chk=chk_db(bbs_no)
    if 'userid' not in session:
        return redirect(url_for('login'))
    elif del_chk[0][3]==session['nickname']:
        del_board_db(bbs_no)
        return '''<script language=javascript>
                  alert('삭제 됐습니다!!') 
                  location.pathname='/board_main'
                    </script>'''
    else:
        return '''<script language=javascript>
             alert('권한이 없습니다!!')
             location.href=history.back();
            </script>'''      

		
def rev_board_db(board_title,board_write,bbs_no):
    db=get_db()
    data=(board_title,board_write,bbs_no)
    sql="update board set bbs_title=%s, bbs_content=%s where bbs_no=%s"
    conn=db.cursor()
    conn.execute(sql,data)
    db.commit()

@app.route('/board_view/revision')
def mod_board():
    bbs_no=request.args.get('bbs_no')
    rv_db=chk_db(bbs_no)
    if 'userid' not in session:
       return redirect(url_for('login'))
    elif session['nickname']==rv_db[0][3]:
        return render_template('revision_write.html',data=rv_db)
    else:
        return '''<script languaget=javascript>
                    alert('권한이 없습니다!!');
                    location.href=history.back();
                    </script>'''

@app.route('/board_view/revision_chk', methods=['POST'])
def rev_chk():
    bbs_no=request.args.get('bbs_no')
    rev_db=chk_db(bbs_no)	
    if request.method=='POST': 
	board_title=request.form.get('board_title_mod')
        board_write=request.form.get('board_write_mod')
        '''if board_title!=0 or board_write==0:
            board_write=[0][2]
	    rev_board_db(board_title=request.form['board_title_mod'],board_write=board_write,bbs_no=bbs_no)
	elif board_title==0 and board_write!=0:
	    board_title=rev_db[0][1]
	    rev_board_db(board_title=board_title,board_write=request.form['board_write_mod'],bbs_no=bbs_no)'''
        if len(board_title)==0 or len(board_write)==0:
	    return ''' <script language=javascript>
		    alert('수정할 값을 입력해주세요!!')
		    location.href=history.back(); 
	 	    </script>'''
	else:
	    rev_board_db(board_title=request.form['board_title_mod'],board_write=request.form['board_write_mod'],bbs_no=bbs_no)
	return redirect(url_for('board_main'))

@app.route('/board_main/search', methods=['GET'])
def board_search():
    query=request.args.get('query')
    search_db=col_search(query)
    if request.method=='GET':
        if 'userid' not in session:
            return redirect(url_for('login'))
        else:    
	    cnt=board_count()
	    return render_template('search_main.html',cnt=len(search_db),data=search_db)
    

def col_search(query):
    db=get_db()
    col_search_sql="show columns from board;"
    conn=db.cursor()
    conn.execute(col_search_sql)
    col_list=conn.fetchall()    
    search_list=tuple()
    i=1

    while 3>=i:
	sql="select * from board where {} like %s".format(col_list[i][0])
	data=('%'+query+'%')	
	conn.execute(sql,data)
	search_list=search_list+conn.fetchall()
	i=i+1
    
    return list(set(search_list))

@app.route('/board_main',methods=['GET'])
def board_main():
    res=get_board()
    if request.method=='GET':
        if 'userid' not in session:
            return redirect(url_for('login'))
        else:    
	    cnt=board_count()
	    return render_template('board_main.html',cnt=cnt[0],data=res)


def board_count():
    db=get_db()
    sql="select count(*) from board;"
    conn=db.cursor()
    conn.execute(sql)
    r_ser=conn.fetchone()
    return r_ser


@app.route('/board_view', methods=['GET'])
def board_view():
    bbs_no=request.args.get('bbs_no')
    view=chk_db(bbs_no)
    if view[0][6]==None:
        file_n="No file"
    else:
        file_n=view[0][6]
    if request.method=='GET':
        if 'userid' not in session:
            return redirect(url_for('login'))
	else: 
            return render_template('board_view.html',view=view,file_n=file_n)
 
@app.route('/board_view/<bbs_no>/<filename>',methods=['GET','POST'])
def filedown(bbs_no,filename):
    return send_from_directory(directory='./uploads',filename=filename)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    else:
        userid=request.form.get('userid')
        userps=request.form.get('userps')
        auth=get_account(userid,userps)
        if len(auth)!=0:
            session['userid']=userid
            session['userps']=userps
            session['nickname']=auth[0][3]
            return redirect(url_for('board_main'))
        else:
            return 'Login Failed'

@app.route('/logout',methods=['GET'])
def logout():
    if request.method=='GET':
        session.clear()
        return redirect(url_for('login'))

if __name__=='__main__':
    app.run(host='0.0.0.0')
