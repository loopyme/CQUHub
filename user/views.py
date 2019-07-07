# -*- coding: utf-8 -*-
import markdown, os, uuid
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.shortcuts import render,redirect
from  django.http  import  HttpResponse
from  django.views.generic import  View  #继承通用类视图
from  django.contrib.auth  import  authenticate,login,logout
from  django.contrib.auth.hashers import make_password  #对数据库进行加密

from  topic.models import Create_Topic
from  operation.models import Topic_Comment
from  .models import User_Info
from  .forms import Login, Register, Info
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL


# Create your views here.

class Login_View(View):
    nav_base = 'nav_base.html'
    def get(self, request):
        forms = Login()
        return render(request, 'user/login.html', {'login': forms})

    def post(self, request):
        forms = Login(request.POST)
        if forms.is_valid():
            user_name = forms.cleaned_data['username']
            pass_word = forms.cleaned_data["password"]
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                login(request, user)
                return redirect(to='topic:index')
            else:
                forms = Login()
                return render(request, 'user/login.html', {'login': forms, 'messsge': '您输入的学号或者密码验证有误'})
        else:
            forms = Login()
            return render(request, 'user/login.html', {'login': forms, 'message': '您输入的信息不全'})


class Revise_View(View):
    def get(self, request):
        forms = Register()
        return render(request, 'user/revise.html', {'forms': forms})

    def post(self, request):
        forms = Revise(request.POST, request.files)
        if forms.is_valid():
            password = forms.cleaned_data["passwordConfirm"]
            password1 = forms.cleaned_data["password"]
            if password != password1:
                return render(request, 'user/revise.html', {'message': '您两次输入的密码不相同', 'forms': forms})
            else:
                nickname = forms.cleaned_data["nickname"]
                user = User_Info()
                user.password = make_password(password)
                user.nickname = nickname
                #!!!
                user.save()
                return redirect('<str:username1>/')
        else:
            return render(request, 'user/revise.html', {'message': '您的信息不符合要求，可能是验证码有误，请您核对信息', 'forms': forms})


class Info_View(View):
    def get(self, request, username):
        forms = Info()
        return render(request, 'user/info.html', {'forms':forms})
    
    def post(self, request, username):
        # user = User_Info.objects.get(username=username)
        forms = Info(request.POST)
        if 'nicknameButton' in request.POST and forms.is_valid():
            print(2**100, '\n', forms, '\n', "0" * 100)
            newNickname = forms.cleaned_data['nickname']
            User_Info.objects.filter(username=username).update(nickname=newNickname)
            forms = Info()
        return render(request, 'user/info.html', {'forms': forms})


def logout_view(request):
    logout(request)
    return redirect(to='topic:index')


class Register_Voew(View):
    def get(self, request):
        forms = Register()
        return render(request, 'user/register.html', {'forms': forms})

    def generate_verify_code(self, student_id):
        res = ""
        code_map = {}
        code = "9128405367"
        for i in range(10):
            code_map[str(i)] = code[i]
        for i in str(hash(str(student_id)) % (3 ** 12)):
            res += code_map[i]
        return res

    def send_verify_mail(self, student_id):
        host_server = 'smtp.exmail.qq.com'
        pwd = 'Djangosucks123'
        sender_mail = 'cquhub-no-reply@mail.loopy.tech'
        receiver = '{}@cqu.edu.cn'.format(student_id)

        mail_title = 'CQU Hub的注册验证'
        mail_content = '''同学你好:

    感谢您使用CQU Hub！
    为确保论坛只对重大学子开放，请确认您的学号为{}，并使用验证码{}来完成您的注册！

CQU Hub开发组
{}'''.format(student_id, self.generate_verify_code(student_id), time.strftime("%Y-%m-%d %X", time.localtime()))

        smtp = SMTP_SSL(host_server)

        smtp.set_debuglevel(0)
        smtp.ehlo(host_server)
        smtp.login(sender_mail, pwd)

        msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_mail
        msg["To"] = receiver
        smtp.sendmail(sender_mail, receiver, msg.as_string())
        smtp.quit()

    def post(self, request):
        forms = Register(request.POST)
        if forms.is_valid():
            username = forms.cleaned_data["username"]
            if User_Info.objects.filter(username=username):
                return render(request, 'user/register.html', {'message': '该学号已经被注册过了!', 'forms': forms})
            password = forms.cleaned_data["passwordConfirm"]
            passwordConfirm = forms.cleaned_data["password"]
            if password != passwordConfirm:
                return render(request, 'user/register.html', {'message': '您两次输入的密码不相同', 'forms': forms})
            nickname = forms.cleaned_data["nickname"]
            avatar = request.FILES.get('avatar', None)
            user = User_Info()
            if avatar != None:
                # 获取上传文件的扩展名
                fileType = os.path.splitext(avatar.name)[1]
                uploadDirPath = os.path.join(
                    os.getcwd(), 'staticfiles/avatar')
                if not os.path.exists(uploadDirPath):
                    os.mkdir(uploadDirPath)
                # 生成唯一文件名
                newName = str(uuid.uuid4()) + fileType
                user.avatarID = newName
                # 拼接要上传的文件在服务器上的全路径
                fileFullPath = uploadDirPath + os.sep + newName
                # 上传文件
                with open(fileFullPath, 'wb+') as fp:
                    for chunk in avatar.chunks():
                        fp.write(chunk)
            user.username = username
            user.password = make_password(password)
            user.nickname = nickname
            user.save()
            login(request, user)
            return redirect(to='topic:index')
        else:
            return render(request, 'user/register.html', {'message': '您的信息不符合要求，可能是验证码有误，请您核对信息', 'forms': forms})


class Info_Profile(View):
    '''
    个人主题数量
    '''
    def  get(self,request,username1,page_id=1):
        userinfo=User_Info.objects.get(username=username1)
        # reservedict1={
        #     '那个谁，我想对你说':'1',
        #     '动手动脚找东西':'2',
        #     'CQU公告':'3',
        #     'CQU身边事':'4',
        #     '技术栏目':'5',
        #     '文学交流':'6',
        #     '论坛公告':'7'
        # }
        # reservedict = {
        #     '1': '那个谁，我想对你说',
        #     '2': '动手动脚找东西',
        #     '3': 'CQU公告',
        #     '4': 'CQU身边事',
        #     '5': '技术栏目',
        #     '6': '文学交流',
        #     '7': '论坛公告'
        # }
        user_theme = userinfo.create_topic_set.all()
        user_reply = userinfo.topic_comment_set.all()
        paginator = Paginator(user_theme, 2)
        page_range = paginator.page_range
        pre_id = page_id-1
        next_id = page_id+1
        if page_id == 1:
            pre_id = 1
        if page_id == len(page_range):
            next_id = page_id
            pre_id = page_id-1
        try:
            user_theme = paginator.page(page_id)
        except  PageNotAnInteger:
            user_theme = paginator.page(1)
        except EmptyPage:
            user_theme = []
        return render(request, 'topic/info_profile.html',
                      {'userinfo': userinfo, 'user_theme': user_theme, 'user_reply': user_reply,'page_id': page_id, 'next_id':next_id, 'pre_id':pre_id,'username':username1})

def Info_page(request, username1, page_id):
    userinfo=User_Info.objects.get(username=username1)
    user_theme = userinfo.create_topic_set.all()
    user_reply = userinfo.topic_comment_set.all()
    paginator = Paginator(user_theme, 2)
    page_range = paginator.page_range
    pre_id = page_id-1
    next_id = page_id+1
    if page_id == 1:
        pre_id = 1
    if page_id == len(page_range):
        next_id = page_id
        pre_id = page_id-1
    try:
        user_theme = paginator.page(page_id)
    except  PageNotAnInteger:
        user_theme = paginator.page(1)
    except EmptyPage:
        user_theme = []
    return render(request, 'topic/info_profile.html',
                    {'userinfo': userinfo, 'user_theme': user_theme, 'user_reply': user_reply,'page_id': page_id, 'next_id':next_id, 'pre_id':pre_id,'username':username1})

def Go_info_page(request, username1):
    userinfo=User_Info.objects.get(username=username1)
    user_theme = userinfo.create_topic_set.all()
    user_reply = userinfo.topic_comment_set.all()
    try:
        page_id = int(request.GET.get('go_info'))
    except:
        page_id = int('cur_page')
    paginator = Paginator(user_theme, 2)
    page_range = paginator.page_range
    max = len(page_range)
    if(page_id > max):
        page_id = int(request.GET.get('cur_page'))
    pre_id = page_id-1
    next_id = page_id+1
    if page_id == 1:
        pre_id = 1
    if page_id == len(page_range):
        next_id = page_id
        pre_id = page_id-1
    try:
        user_theme = paginator.page(page_id)
    except  PageNotAnInteger:
        user_theme = paginator.page(1)
    except EmptyPage:
        user_theme = []
    return render(request, 'topic/info_profile.html',
                    {'userinfo': userinfo, 'user_theme': user_theme, 'user_reply': user_reply,'page_id': page_id, 'next_id':next_id, 'pre_id':pre_id,'username':username1})


class Info_Reply(View):
    def get(self, request, username1):
        userinfo = User_Info.objects.get(username=username1)
        user_reply = userinfo.topic_comment_set.all()
        for each_user_reply in user_reply:
            reply = each_user_reply.content
            markdown_comment = markdown.markdown(
                reply,
                extensions=[
                    'markdown.extensions.extra',
                    'markdown.extensions.codehilite',
                    'markdown.extensions.toc',
                ]
            )
            each_user_reply.content = markdown_comment

        return render(request, 'topic/info_reply.html', {'userinfo': userinfo, 'all_user_reply': user_reply})


def upload(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        avatar = request.FILES.get('avatar')
        with open(avatar.name, 'wb') as f:
            for line in avatar:
                f.write(line)
        return HttpResponse('ok')
    return redirect(to='user:register')
