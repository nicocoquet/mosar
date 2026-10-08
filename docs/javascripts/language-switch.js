/* Mosar — FR | EN, using URLs produced by mkdocs-static-i18n. */
(function () {
  function installLanguageSwitch() {
    const header = document.querySelector(".md-header__inner");
    if (!header || header.querySelector(".mosar-language-switch")) return;

    const nativeLinks = Array.from(
      header.querySelectorAll(".md-select__link[hreflang]")
    );
    const urls = {};
    for (const link of nativeLinks) {
      const lang = link.getAttribute("hreflang").toLowerCase().split("-")[0];
      if ((lang === "fr" || lang === "en") && link.href) urls[lang] = link.href;
    }
    // Never guess a translated URL: use only the plugin-generated links.
    if (!urls.fr || !urls.en) return;

    const current = document.documentElement.lang.toLowerCase().split("-")[0];
    const switcher = document.createElement("nav");
    switcher.className = "mosar-language-switch";
    switcher.setAttribute("aria-label", current === "en" ? "Language" : "Langue");

    for (const lang of ["fr", "en"]) {
      if (lang === "en") {
        const divider = document.createElement("span");
        divider.className = "mosar-language-divider";
        divider.textContent = "|";
        divider.setAttribute("aria-hidden", "true");
        switcher.appendChild(divider);
      }
      const link = document.createElement("a");
      link.href = urls[lang];
      link.hreflang = lang;
      link.lang = lang;
      link.textContent = lang.toUpperCase();
      link.setAttribute("aria-label", lang === "fr" ? "Français" : "English");
      if (current === lang) link.setAttribute("aria-current", "page");
      switcher.appendChild(link);
    }

    const search = header.querySelector(".md-search");
    if (search) search.insertAdjacentElement("afterend", switcher);
    else header.appendChild(switcher);
    document.documentElement.classList.add("mosar-language-ready");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installLanguageSwitch);
  } else {
    installLanguageSwitch();
  }
})();
