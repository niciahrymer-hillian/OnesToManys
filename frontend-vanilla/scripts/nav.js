(function () {
  function closeMenu(menu) {
    menu.classList.remove("is-open");
  }

  function initPancakeMenu(currentPage) {
    const menu = document.getElementById("pancakeMenu");
    const toggle = document.getElementById("menuToggle");
    if (!menu || !toggle) {
      return;
    }

    menu.querySelectorAll("a").forEach((link) => {
      if (link.dataset.page === currentPage) {
        link.classList.add("is-active");
      }
      link.addEventListener("click", () => closeMenu(menu));
    });

    toggle.addEventListener("click", () => {
      menu.classList.toggle("is-open");
    });

    document.addEventListener("click", (event) => {
      if (!menu.contains(event.target) && !toggle.contains(event.target)) {
        closeMenu(menu);
      }
    });
  }

  window.initPancakeMenu = initPancakeMenu;
})();
