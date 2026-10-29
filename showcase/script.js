(function () {
  var APP_URL = 'app/';

  var texts = {
    es: {
      hint: 'Haz clic y juega con las flechas, Espacio y Esc.',
      subtitle: 'Juego de bloques que caen, en Python',
      intro: 'Juego clásico de bloques que caen, hecho desde cero con Pygame: rotación con ajuste a las paredes, caída rápida y niveles que aceleran. Es el mismo código Python del juego de escritorio, ejecutándose en el navegador.',
      notice_title: 'Versión web del juego',
      notice_wasm: 'El juego se compila a WebAssembly con pygbag: la primera carga descarga el intérprete de Python y puede tardar unos segundos.',
      notice_tap: 'Toca o haz clic en el juego para empezar; el navegador necesita ese gesto para activar la música.',
      notice_controls: 'En el ordenador se juega con el teclado. En el móvil, con los botones bajo el tablero (mantén pulsadas las flechas para moverte más rápido).',
      code: 'Código y descarga',
      fullscreen: 'Pantalla completa',
      games: 'Juegos',
      view_demo: 'Jugar'
    },
    en: {
      hint: 'Click, then play with the arrows, Space and Esc.',
      subtitle: 'Falling blocks game, in Python',
      intro: 'Classic falling blocks game built from scratch with Pygame: rotation with wall kicks, hard drop and levels that speed up. It is the same Python code as the desktop game, running in the browser.',
      notice_title: 'Web version of the game',
      notice_wasm: 'The game is compiled to WebAssembly with pygbag: the first load downloads the Python interpreter and may take a few seconds.',
      notice_tap: 'Tap or click the game to start; the browser needs that gesture to enable the music.',
      notice_controls: 'On a computer you play with the keyboard. On a phone, with the buttons below the board (hold the arrows to move faster).',
      code: 'Code & download',
      fullscreen: 'Full screen',
      games: 'Games',
      view_demo: 'Play'
    }
  };

  // --- Idioma: misma preferencia que la web (localStorage 'lang') ---

  function readLang() {
    try {
      var stored = localStorage.getItem('lang');
      if (stored === 'es' || stored === 'en') return stored;
    } catch (e) {}
    return (navigator.language || '').slice(0, 2).toLowerCase() === 'es' ? 'es' : 'en';
  }

  var lang = readLang();

  function t(key) { return texts[lang][key] || texts.es[key] || key; }

  function applyLang() {
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll('.lang button').forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.lang === lang));
    });
  }

  document.querySelectorAll('.lang button').forEach(function (button) {
    button.addEventListener('click', function () {
      lang = button.dataset.lang;
      try { localStorage.setItem('lang', lang); } catch (e) {}
      applyLang();
    });
  });

  // --- Ficha compartida ---

  var template = document.getElementById('info');
  document.querySelectorAll('[data-info]').forEach(function (slot) {
    slot.appendChild(template.content.cloneNode(true));
  });

  // --- Una sola instancia de la app: en el marco o a pantalla completa ---

  var mobileQuery = window.matchMedia('(max-width: 760px), (max-height: 560px)');
  var desktopFrame = document.getElementById('desktop-app');
  var mobileFrame = document.getElementById('mobile-app');

  function mountApp() {
    var active = mobileQuery.matches ? mobileFrame : desktopFrame;
    var inactive = mobileQuery.matches ? desktopFrame : mobileFrame;
    if (inactive.getAttribute('src')) inactive.removeAttribute('src');
    if (!active.getAttribute('src')) active.setAttribute('src', APP_URL);
  }

  mountApp();
  mobileQuery.addEventListener('change', mountApp);

  // --- Hoja de información (móvil): se muestra una vez por sesión ---

  var sheet = document.querySelector('.sheet');
  var backdrop = document.querySelector('.sheet-backdrop');

  function setSheet(open) {
    sheet.classList.toggle('open', open);
    backdrop.classList.toggle('open', open);
  }

  document.querySelectorAll('[data-open-sheet]').forEach(function (el) {
    el.addEventListener('click', function () { setSheet(true); });
  });
  document.querySelectorAll('[data-close-sheet]').forEach(function (el) {
    el.addEventListener('click', function () { setSheet(false); });
  });

  if (mobileQuery.matches) {
    var seen = false;
    try { seen = sessionStorage.getItem('blockfall-demo-sheet') === '1'; } catch (e) {}
    if (!seen) {
      setSheet(true);
      try { sessionStorage.setItem('blockfall-demo-sheet', '1'); } catch (e) {}
    }
  }

  applyLang();
})();
