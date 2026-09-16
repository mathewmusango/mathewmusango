/* ==========================================================================
   GitHub hub renderer.
   Every number rendered here comes from window.PROFILE — the snapshot in
   data/profile.js, refreshed by scripts/fetch_profile.py. The markup in
   index.html is a static fallback: this script replaces the data panels.
   ========================================================================== */

(() => {
  "use strict";

  const data = window.PROFILE;

  if (!data) {
    console.warn("profile data missing — run: python3 scripts/fetch_profile.py");
    return;
  }

  /* ------------------------------------------------------------ helpers -- */

  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const DAY = 86400000;
  const utcDate = (iso) => new Date(iso + "T00:00:00Z");

  // Inline icons. Each one carries its own fill/stroke so CSS only sizes it.
  const ICON = {
    location:
      '<svg class="gh-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M8 1.4A5.1 5.1 0 0 1 13.1 6.5c0 3.7-5.1 8.1-5.1 8.1S2.9 10.2 2.9 6.5A5.1 5.1 0 0 1 8 1.4Zm0 7.1a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"/></svg>',
    building:
      '<svg class="gh-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M2.5 2h11a1 1 0 0 1 1 1v11h-5v-3h-3v3h-5V3a1 1 0 0 1 1-1Zm2.5 2.5h1.5V6H5V4.5Zm4 0H11V6H9V4.5Zm-4 3h1.5V9H5V7.5Zm4 0H11V9H9V7.5Z"/></svg>',
    calendar:
      '<svg class="gh-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M4.5 1a.8.8 0 0 1 .8.8V3h5.4V1.8a.8.8 0 1 1 1.6 0V3h.7A1.5 1.5 0 0 1 14.5 4.5v8A1.5 1.5 0 0 1 13 14H3a1.5 1.5 0 0 1-1.5-1.5v-8A1.5 1.5 0 0 1 3 3h.7V1.8A.8.8 0 0 1 4.5 1Zm7.4 5.5h-9v6h9Z"/></svg>',
    users:
      '<svg class="gh-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M6 7.5a2.75 2.75 0 1 0 0-5.5 2.75 2.75 0 0 0 0 5.5Zm0 1.3c2.5 0 4.5 1.7 4.5 3.8V14h-9v-1.4c0-2.1 2-3.8 4.5-3.8Zm5.1-6.4a2.3 2.3 0 0 1 0 4.6V6.3a1 1 0 0 0 0-2Zm.6 5.7c1.6.3 2.8 1.5 2.8 3.1V14h-2.2v-1.4c0-1.2-.3-2.2-.8-3Z"/></svg>',
    star: '<svg class="gh-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M8 1.3l1.9 4.2 4.6.6-3.4 3.2.9 4.6L8 11.8l-4 2.1.9-4.6L1.5 6.1l4.6-.6Z"/></svg>',
    fork: '<svg class="gh-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M4 1.2a2.2 2.2 0 0 1 .8 4.25v1.3c0 .6.4 1 1 1h4.4c.6 0 1-.4 1-1v-1.3a2.2 2.2 0 1 1 1.6 0v1.3a2.6 2.6 0 0 1-2.6 2.6H8.7v1.2a2.2 2.2 0 1 1-1.6 0v-1.2H5.8A2.6 2.6 0 0 1 3.2 7.75v-1.3A2.2 2.2 0 0 1 4 1.2Z"/></svg>',
    issue:
      '<svg class="gh-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M8 2.2a5.8 5.8 0 1 0 0 11.6A5.8 5.8 0 0 0 8 2.2Zm0 1.6a4.2 4.2 0 1 1 0 8.4 4.2 4.2 0 0 1 0-8.4Zm0 1.7a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z"/></svg>',
    github:
      '<svg class="gh-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M8 1.3a6.9 6.9 0 0 0-2.2 13.4c.35.06.47-.15.47-.33v-1.2c-1.9.42-2.3-.9-2.3-.9-.32-.8-.77-1.02-.77-1.02-.63-.43.05-.42.05-.42.7.05 1.06.72 1.06.72.62 1.06 1.62.75 2.02.57.06-.45.24-.75.44-.92-1.53-.17-3.13-.76-3.13-3.4 0-.75.27-1.37.71-1.85-.07-.17-.31-.87.07-1.82 0 0 .58-.19 1.9.7a6.6 6.6 0 0 1 3.46 0c1.32-.89 1.9-.7 1.9-.7.38.95.14 1.65.07 1.82.44.48.71 1.1.71 1.85 0 2.65-1.61 3.23-3.14 3.4.25.21.47.63.47 1.27v1.88c0 .18.12.4.48.33A6.9 6.9 0 0 0 8 1.3Z"/></svg>',
    link: '<svg class="gh-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M6.5 3.5H3.8A1.3 1.3 0 0 0 2.5 4.8v7.4a1.3 1.3 0 0 0 1.3 1.3h7.4a1.3 1.3 0 0 0 1.3-1.3V9.5"/><path d="M9.5 2.5h4v4"/><path d="M13.2 2.8 7.5 8.5"/></svg>',
  };

  function el(tag, props = {}, children = []) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(props)) {
      if (value === null || value === undefined || value === "") continue;
      if (key === "text") node.textContent = value;
      else node.setAttribute(key, value);
    }
    for (const child of [].concat(children)) {
      if (child) node.appendChild(child);
    }
    return node;
  }

  function icon(markup) {
    const wrap = document.createElement("span");
    wrap.innerHTML = markup; // static, developer-authored markup only
    return wrap.firstElementChild;
  }

  function compact(value) {
    if (value < 1000) return String(value);
    if (value < 10000) return value.toLocaleString("en-US");
    if (value < 1000000) return (value / 1000).toFixed(1).replace(/\.0$/, "") + "k";
    return (value / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
  }

  function monthYear(iso) {
    return utcDate(iso).toLocaleDateString("en-GB", {
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    });
  }

  function dayLong(date) {
    return date.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    });
  }

  const render = (name) => document.querySelector('[data-render="' + name + '"]');

  /* --------------------------------------------------------- static bits -- */

  // The avatar's extension depends on what GitHub served, so the favicon is
  // pointed at the same file the snapshot records.
  const favicon = document.createElement("link");
  favicon.rel = "icon";
  favicon.href = data.user.avatar;
  document.head.appendChild(favicon);

  for (const node of document.querySelectorAll("[data-fill]")) {
    const key = node.dataset.fill;
    if (key === "name") node.textContent = data.user.name;
    if (key === "handle") node.textContent = "@" + data.user.login;
    if (key === "generated") {
      node.textContent = dayLong(new Date(data.generated));
      node.setAttribute("datetime", data.generated);
    }
  }

  /* -------------------------------------------------------------- stats -- */

  const statLabels = [
    ["repos", "Total repos"],
    ["stars", "All stars"],
    ["followers", "Followers"],
    ["years_active", "Years active"],
  ];

  const statsHost = render("stats");
  if (statsHost) {
    for (const [key, label] of statLabels) {
      statsHost.appendChild(
        el("div", { class: "stat" }, [
          el("span", { class: "stat__value", text: compact(data.stats[key]) }),
          el("span", { class: "stat__label", text: label }),
        ])
      );
    }
  }

  /* ------------------------------------------------------------- profile -- */

  const profileHost = render("profile");
  if (profileHost) {
    const user = data.user;
    const rows = [];

    if (user.company) {
      rows.push(el("div", { class: "profile__row" }, [icon(ICON.building), el("span", { text: user.company })]));
    }
    if (user.location) {
      rows.push(el("div", { class: "profile__row" }, [icon(ICON.location), el("span", { text: user.location })]));
    }
    rows.push(
      el("div", { class: "profile__row" }, [
        icon(ICON.calendar),
        el("span", { text: "Joined " + monthYear(user.joined) }),
      ])
    );
    rows.push(
      el("div", { class: "profile__row" }, [
        icon(ICON.users),
        el("span", {
          text: compact(user.followers) + (user.followers === 1 ? " follower" : " followers"),
        }),
      ])
    );
    rows.push(
      el("div", { class: "profile__row" }, [
        icon(ICON.github),
        el("span", { text: "Following " + compact(user.following) }),
      ])
    );

    profileHost.appendChild(
      el("img", {
        class: "profile__avatar",
        src: user.avatar,
        alt: user.name,
        width: "88",
        height: "88",
        loading: "lazy",
      })
    );
    profileHost.appendChild(el("h2", { class: "profile__name", text: user.name }));
    profileHost.appendChild(el("p", { class: "profile__handle", text: "@" + user.login }));
    if (user.bio) {
      profileHost.appendChild(el("p", { class: "profile__bio", text: user.bio }));
    }
    profileHost.appendChild(
      el("div", { class: "profile__actions" }, [
        (() => {
          const link = el("a", {
            class: "btn btn--primary",
            href: user.profile_url,
            rel: "me",
            text: "Follow on GitHub",
          });
          return link;
        })(),
      ])
    );
    profileHost.appendChild(el("div", { class: "profile__rows" }, rows));
  }

  /* ---------------------------------------------------------------- tech -- */

  const techHost = render("tech");
  if (techHost) {
    const head = el("div", { class: "panel__head" }, [
      el("h2", { class: "panel__title", text: "Tech Stack & Languages" }),
      el("span", { class: "panel__meta", text: "By bytes committed" }),
    ]);

    const chips = el("ul", { class: "chips" });
    for (const tech of data.core_tech) {
      chips.appendChild(el("li", { class: "chip", text: tech }));
    }

    const bars = el("div", { class: "bars" });
    for (const language of data.languages) {
      bars.appendChild(
        el("div", { class: "bar" }, [
          el("div", { class: "bar__row" }, [
            el("span", { class: "bar__name", text: language.name }),
            el("span", { class: "bar__pct", text: language.pct.toFixed(1) + "%" }),
          ]),
          el("div", { class: "bar__track" }, [
            el("div", {
              class: "bar__fill",
              style: "width: " + Math.max(language.pct, 1.5) + "%",
            }),
          ]),
        ])
      );
    }

    techHost.appendChild(head);
    techHost.appendChild(el("p", { class: "tech__label", text: "Core technologies" }));
    techHost.appendChild(chips);
    techHost.appendChild(el("p", { class: "tech__label", text: "Languages" }));
    techHost.appendChild(bars);
  }

  /* ------------------------------------------------------- contributions -- */

  const heatHost = render("contributions");
  if (heatHost) {
    const contrib = data.contributions;
    const start = utcDate(contrib.start);
    const lead = start.getUTCDay(); // 0 = Sunday
    const columns = Math.ceil((lead + contrib.days) / 7);
    const levels = contrib.levels.split("");

    heatHost.appendChild(
      el("div", { class: "panel__head" }, [
        el("h2", { class: "panel__title", text: "Contributions" }),
        el("span", { class: "panel__meta", text: compact(contrib.total) + " in the last year" }),
      ])
    );

    // Month labels sit above the column where each new month starts.
    const months = el("div", { class: "heat__months", "aria-hidden": "true" });
    let seenMonth = null;
    for (let column = 0; column < columns; column++) {
      const lastDay = new Date(start.getTime() + (column * 7 - lead + 6) * DAY);
      const month = lastDay.getUTCMonth();
      if (column === 0 || month !== seenMonth) {
        months.appendChild(el("span", { class: "heat__month", text: MONTHS[month] }));
        seenMonth = month;
      } else {
        months.appendChild(el("span", { class: "heat__month" }));
      }
    }

    const grid = el("div", {
      class: "heat",
      role: "img",
      "aria-label":
        compact(contrib.total) + " contributions in the last year, from " + dayLong(start),
    });
    for (let i = 0; i < lead; i++) {
      grid.appendChild(el("div", { class: "heat__cell heat__cell--pad" }));
    }
    levels.forEach((level, index) => {
      const date = new Date(start.getTime() + index * DAY);
      const count = contrib.counts[index];
      grid.appendChild(
        el("div", {
          class: "heat__cell",
          "data-level": level,
          title:
            count === 0
              ? "No contributions on " + dayLong(date)
              : count + (count === 1 ? " contribution" : " contributions") + " on " + dayLong(date),
        })
      );
    });

    const legend = el("div", { class: "heat__legend", "aria-hidden": "true" }, [
      el("span", { text: "Less" }),
    ]);
    for (let level = 0; level <= 4; level++) {
      legend.appendChild(el("div", { class: "heat__cell", "data-level": String(level) }));
    }
    legend.appendChild(el("span", { text: "More" }));

    heatHost.appendChild(months);

    const scroll = el("div", { class: "heat__scroll" }, [months, grid]);

    heatHost.appendChild(scroll);
    heatHost.appendChild(legend);
  }

  /* ----------------------------------------------------------- projects -- */

  const projectHost = render("projects");
  if (projectHost) {
    projectHost.appendChild(
      el("div", { class: "projects__head" }, [
        el("h2", { class: "panel__title", text: "Notable Projects" }),
        el("span", { class: "panel__meta", text: "Most stars" }),
      ])
    );

    const grid = el("div", { class: "projects__grid" });
    for (const project of data.projects) {
      const title = el("h3", { class: "project__name" }, [
        el("a", { href: project.url, text: project.name }),
      ]);
      const desc = el("p", {
        class: "project__desc",
        text: project.description || "No description yet.",
      });

      const foot = el("div", { class: "project__foot" });
      if (project.language) {
        foot.appendChild(
          el("span", { class: "project__stat" }, [
            el("span", { class: "lang-dot" }),
            el("span", { text: project.language }),
          ])
        );
      }
      foot.appendChild(
        el("span", { class: "project__stat", title: compact(project.stars) + " stars" }, [
          icon(ICON.star),
          el("span", { text: compact(project.stars) }),
        ])
      );
      foot.appendChild(
        el("span", { class: "project__stat", title: compact(project.forks) + " forks" }, [
          icon(ICON.fork),
          el("span", { text: compact(project.forks) }),
        ])
      );
      foot.appendChild(
        el("span", { class: "project__stat", title: compact(project.issues) + " open issues" }, [
          icon(ICON.issue),
          el("span", { text: compact(project.issues) }),
        ])
      );
      if (project.homepage) {
        foot.appendChild(
          el("span", { class: "project__stat" }, [
            el("a", { href: project.homepage, title: "Live site", text: "Live" }),
            icon(ICON.link),
          ])
        );
      }

      grid.appendChild(el("div", { class: "project" }, [title, desc, foot]));
    }

    projectHost.appendChild(grid);
  }
})();
