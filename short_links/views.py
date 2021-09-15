from django.contrib import messages
from django.core.cache import cache
from django.core.validators import slug_re
from django.shortcuts import redirect
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.views import View
from django.views.generic import ListView

from links.settings import CACHES_TTL
import logging
from .models import ShortLinks

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Redirect(View):
    def get(self, request, slug):
        try:
            # Прочитаем ссылку из кеша, если запись существует
            # Иначе прочитаем из базы и добавим в кеш
            if cache.keys(slug):
                logger.debug(f'Redirect from cache.')
                return redirect(cache.get(slug))
            elif ShortLinks.objects.filter(user_subpart=slug):
                logger.debug(f'Rare link. Adding record to cahce.')
                long_link = ShortLinks.objects.filter(user_subpart=slug)[0].long_link
                cache.set(slug, long_link, timeout=CACHES_TTL)
                return redirect(long_link)
            else:
                logger.debug('Trying redirect noexistent link!')
                messages.error(request, f'Ссылка "{slug}" не существует.')
        except NoReverseMatch:
            messages.error(request, f'Конечная Ссылка для перенаправления по "{slug}" некорректна или недоступна.')
            logger.warning('Lin ib BD incorrect. Redirection failed.')
        else:
            logger.info('Redirect successful.')
        return redirect(reverse('main'))

class MainView(ListView):
    paginate_by = 4  # Для удобства тестирования выводим по 4 записи на странице
    model = ShortLinks
    template_name = 'index.html'

    def get_queryset(self):
        '''
        Отображаем только записи данного пользователи, сортировка по дате создания.
        '''
        qs = ShortLinks.objects.filter(session_id=self.request.session.session_key).order_by('-date_time')
        return qs
    
    def post(self, request):
        long_link = request.POST['link'] 
        subpart = request.POST['subpart']
        
        # Создаем сессию, если пользователь новый
        if request.session.session_key is None:
            request.session.create()
        
        # Проверяем наличие длинной ссылки.
        if not long_link:
            messages.error(request, 'Поле с длинной ссылкой не может быть пустым')
        
        else: 
            # Проверка, что пользовательский короткий путь введен и корретен
            if subpart and not slug_re.match(subpart):
                messages.error(
                    request,
                    'Недопустимые символы в коротком пути. ' +
                    'Допустимые символы: "Aa-Zz", "0-9", "-", "_". ' +
                    'Попробуйте еще раз.'
                    )
            # Проверка, что пользовательский короткий путь введен и не занят
            elif subpart and ShortLinks.objects.filter(user_subpart=subpart):
                messages.error(
                    request, 
                    'Такой Короткий путь уже занят. Укажите другой или оставьте поле пустым.'
                    )
            else:
                # Создание записи
                try:
                    record = ShortLinks.objects.create(
                        long_link=long_link,
                        session_id=request.session.session_key
                        )
                    record.user_subpart = subpart or record.id
                    record.save()
                except Exception as err:
                    logger.error(f'Record creation error: {err}')
                else:
                    logger.info('New link added.')
        return redirect(reverse('main'))