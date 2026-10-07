(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const lockScroll = (lock) => {
    document.documentElement.style.overflow = lock ? 'hidden' : '';
  };

  /* ---------- Шапка: тень при прокрутке ---------- */
  const header = $('[data-header]');
  if (header) {
    const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 10);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---------- Мобильное меню ---------- */
  const burger = $('[data-burger]');
  if (burger) {
    const setOpen = (open) => {
      document.body.classList.toggle('nav-open', open);
      burger.setAttribute('aria-expanded', String(open));
      lockScroll(open);
    };
    burger.addEventListener('click', () => setOpen(!document.body.classList.contains('nav-open')));
    $$('[data-nav] a').forEach((a) => a.addEventListener('click', () => setOpen(false)));
    document.addEventListener('keydown', (e) => e.key === 'Escape' && setOpen(false));
  }

  /* ---------- Слайдер героя ---------- */
  const slider = $('[data-slider]');
  if (slider) {
    const texts = $$('[data-slide]', slider);
    const bgs = $$('[data-slide-bg]', slider);
    const dotsBox = $('[data-dots]', slider);
    const delay = 6500;
    let index = 0;
    let timer;

    const dots = texts.map((_, i) => {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'hero__dot';
      dot.setAttribute('aria-label', `Слайд ${i + 1}`);
      dot.addEventListener('click', () => go(i));
      dotsBox && dotsBox.appendChild(dot);
      return dot;
    });
    const go = (i) => {
      index = (i + texts.length) % texts.length;
      texts.forEach((el, n) => el.classList.toggle('is-active', n === index));
      bgs.forEach((el, n) => el.classList.toggle('is-active', n === index));
      dots.forEach((dot, n) => dot.classList.toggle('is-active', n === index));
      clearTimeout(timer);
      if (texts.length > 1) timer = setTimeout(() => go(index + 1), delay);
    };

    let startX = null;
    slider.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; }, { passive: true });
    slider.addEventListener('touchend', (e) => {
      if (startX === null) return;
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 60 && !e.target.closest('form')) go(index + (dx < 0 ? 1 : -1));
      startX = null;
    });
    go(0);
  }

  /* ---------- Отложенные картинки: data-src грузим позже, чтобы не мешать первому экрану ---------- */
  const loadImg = (img) => {
    if (img.dataset.srcset) img.srcset = img.dataset.srcset;
    if (img.dataset.src) img.src = img.dataset.src;
    img.removeAttribute('data-src');
    img.removeAttribute('data-srcset');
  };
  const lazyImgs = $$('img[data-lazy]');
  if ('IntersectionObserver' in window) {
    const lio = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { loadImg(e.target); lio.unobserve(e.target); } });
    }, { rootMargin: '400px 0px' });
    lazyImgs.forEach((img) => lio.observe(img));
  } else {
    lazyImgs.forEach(loadImg);
  }
  const loadRestSlides = () => setTimeout(() => $$('img[data-slide-bg][data-src]').forEach(loadImg), 1500);
  if (document.readyState === 'complete') loadRestSlides(); else window.addEventListener('load', loadRestSlides);

  /* ---------- Появление при скролле ---------- */
  const revealEls = $$('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach((el) => {
      // соседние карточки появляются одна за другой
      const siblings = el.parentElement ? [...el.parentElement.children].filter((c) => c.matches('.reveal')) : [];
      const pos = siblings.indexOf(el);
      if (pos > 0) el.style.transitionDelay = `${Math.min(pos, 4) * 80}ms`;
      io.observe(el);
    });
  } else {
    revealEls.forEach((el) => el.classList.add('is-visible'));
  }

  /* ---------- Даты: не раньше сегодня, выезд после заезда ---------- */
  const isoDate = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  const linkDates = (checkIn, checkOut) => {
    if (!checkIn || !checkOut) return;
    checkIn.min = isoDate(new Date());
    const sync = () => {
      const base = checkIn.value ? new Date(checkIn.value) : new Date();
      base.setDate(base.getDate() + 1);
      checkOut.min = isoDate(base);
      if (checkOut.value && checkOut.value < checkOut.min) checkOut.value = checkOut.min;
    };
    checkIn.addEventListener('change', sync);
    sync();
  };
  const bar = $('[data-booking-bar]');
  if (bar) linkDates($('[name=check_in]', bar), $('[name=check_out]', bar));

  /* ---------- Форма брони: предварительный расчёт ---------- */
  const bookingForm = $('[data-booking-form]');
  const ratesEl = $('#room-rates');
  if (bookingForm && ratesEl) {
    const rates = JSON.parse(ratesEl.textContent);
    const f = (name) => $(`[name=${name}]`, bookingForm);
    const out = (name) => $(`[data-est-${name}]`);
    const money = (n) => n.toLocaleString('ru-RU') + ' сом';
    linkDates(f('check_in'), f('check_out'));

    const calc = () => {
      const room = rates[f('room').value];
      const withMeals = f('with_meals').checked;
      const adults = parseInt(f('adults').value, 10) || 1;
      const inDate = f('check_in').value ? new Date(f('check_in').value) : null;
      const outDate = f('check_out').value ? new Date(f('check_out').value) : null;
      const nights = inDate && outDate ? Math.round((outDate - inDate) / 864e5) : 0;

      out('room').textContent = room ? room.name : '—';
      out('nights').textContent = nights > 0 ? nights : '—';
      if (!room || !room.rates.length) {
        out('rate').textContent = '—';
        out('total').textContent = '—';
        return;
      }
      // Тариф, рассчитанный на ближайшее к числу взрослых количество гостей
      const rate = [...room.rates].sort((a, b) => Math.abs(a.guests - adults) - Math.abs(b.guests - adults))[0];
      const price = withMeals ? rate.full : (rate.room || rate.full);
      out('rate').textContent = `${money(price)} (${rate.guests} чел.)`;
      out('total').textContent = nights > 0 ? money(price * nights) : '—';
    };
    bookingForm.addEventListener('input', calc);
    bookingForm.addEventListener('change', calc);
    calc();
  }

  /* ---------- Табы ---------- */
  $$('[data-tabs]').forEach((tabs) => {
    const buttons = $$('[data-tab]', tabs);
    buttons.forEach((btn) => btn.addEventListener('click', () => {
      buttons.forEach((b) => b.classList.toggle('is-active', b === btn));
      $$('[data-panel]', tabs).forEach((panel) => {
        const active = panel.dataset.panel === btn.dataset.tab;
        panel.classList.toggle('is-active', active);
        panel.hidden = !active;
      });
    }));
  });

  /* ---------- Фильтр галереи ---------- */
  const filter = $('[data-filter]');
  if (filter) {
    const items = $$('.gallery-grid__item');
    filter.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-filter-value]');
      if (!btn) return;
      $$('[data-filter-value]', filter).forEach((b) => b.classList.toggle('is-active', b === btn));
      const value = btn.dataset.filterValue;
      items.forEach((item) => {
        item.hidden = value !== 'all' && item.dataset.category !== value;
        if (!item.hidden && item.animate && !reduceMotion) {
          item.animate([{ opacity: 0, transform: 'scale(.96)' }, { opacity: 1, transform: 'none' }], { duration: 500, easing: 'cubic-bezier(.22,1,.36,1)' });
        }
      });
    });
  }

  /* ---------- Лайтбокс ---------- */
  const links = $$('[data-lightbox]');
  if (links.length) {
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.innerHTML = `
      <figure class="lightbox__figure"><img class="lightbox__img" alt=""><figcaption class="lightbox__caption"></figcaption></figure>
      <button class="lightbox__btn lightbox__close" type="button" aria-label="Закрыть"><svg class="icon"><use href="#i-close"/></svg></button>
      <button class="lightbox__btn lightbox__prev" type="button" aria-label="Назад"><svg class="icon"><use href="#i-chevron-left"/></svg></button>
      <button class="lightbox__btn lightbox__next" type="button" aria-label="Вперёд"><svg class="icon"><use href="#i-chevron-right"/></svg></button>`;
    document.body.appendChild(box);
    const img = $('.lightbox__img', box);
    const caption = $('.lightbox__caption', box);
    let group = [];
    let current = 0;

    const show = (i) => {
      current = (i + group.length) % group.length;
      img.src = group[current].href;
      caption.textContent = group[current].dataset.caption || '';
    };
    const open = (link) => {
      const root = link.closest('[data-lightbox-group]') || document;
      group = $$('[data-lightbox]', root).filter((a) => !a.hidden);
      show(group.indexOf(link));
      box.classList.add('is-open');
      lockScroll(true);
    };
    const close = () => {
      box.classList.remove('is-open');
      lockScroll(false);
    };

    links.forEach((link) => link.addEventListener('click', (e) => { e.preventDefault(); open(link); }));
    $('.lightbox__close', box).addEventListener('click', close);
    $('.lightbox__prev', box).addEventListener('click', () => show(current - 1));
    $('.lightbox__next', box).addEventListener('click', () => show(current + 1));
    box.addEventListener('click', (e) => { if (e.target === box) close(); });
    document.addEventListener('keydown', (e) => {
      if (!box.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(current - 1);
      if (e.key === 'ArrowRight') show(current + 1);
    });
  }

  /* ---------- Тосты ---------- */
  $$('.toast').forEach((toast) => {
    const hide = () => toast.remove();
    $('.toast__close', toast)?.addEventListener('click', hide);
    setTimeout(hide, 7000);
  });
})();
