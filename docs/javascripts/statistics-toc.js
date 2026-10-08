(function () {
  function updateStatisticsToc() {
    const path = window.location.pathname.replace(/\/+$/, "/");

    const isFrench = /\/statistiques\/$/.test(path);
    const isEnglish = /\/en\/statistiques\/$/.test(path);

    if (!isFrench && !isEnglish) return;

    const title = document.querySelector(
      ".md-sidebar--secondary .md-nav--secondary .md-nav__title"
    );

    if (!title) return;

    title.textContent = isEnglish
      ? "List of charts"
      : "Liste des graphiques";
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", updateStatisticsToc);
  } else {
    updateStatisticsToc();
  }
})();