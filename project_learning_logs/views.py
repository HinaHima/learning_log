from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.http import Http404

def index(request):
    """Домашняя страница проекта project_learning_log"""
    return render(request, 'project_learning_logs/index.html')

def check(request, topic):
    if topic.owner != request.user:
        raise Http404

@login_required
def topics(request):
    """Выводит список тем."""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics' : topics}
    return render(request, 'project_learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Выводит одну тему и все ее записи."""
    topic = Topic.objects.get(id=topic_id)
    #Проверка принадлежности темы текущему пользователю.
    check(request, topic)

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic' : topic, 'entries' : entries}
    return render(request, 'project_learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Определяет новую тему."""
    if request.method != 'POST':
        #Данные не отправлялись; создается пустая форма.
        form = TopicForm()
    else:
        #Отправленные данные POST; обработать данные.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('project_learning_logs:topics')

    #Вывести пустую или недействительную форму.
    context = {'form' : form}
    return render(request, 'project_learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме."""
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        #Данные не отправлялись; создается пустая форма.
        form = EntryForm()
    else:
        #Отправляемые данные POST; обработать данные.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            if topic.owner != request.user:
                raise Http404
            new_entry.save()
            return redirect('project_learning_logs:topic', topic_id=topic_id)

    #Вывести пустую или недействительную форму.
    context = {'topic' : topic, 'form' : form}
    return render(request, 'project_learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check(request, topic)

    if request.method != 'POST':
        #Исходный запрос; форма заполняется данными текущей записи.
        form = EntryForm(instance=entry)
    else:
        # Отправка данных POST; обработка данных.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_learning_logs:topic', topic_id=topic.id)

    context = {'entry' : entry, 'topic' : topic, 'form' : form}
    return render(request, 'project_learning_logs/edit_entry.html', context)

