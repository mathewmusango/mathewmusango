/* ==========================================================================
   GitHub hub renderer.

   Numbers are painted from window.PROFILE (the committed snapshot in
   data/profile.js) and then, when the API answers, repainted from live data
   fetched straight from GitHub's public REST API. The contribution calendar
   has no public client-side endpoint, so it always comes from the snapshot —
   the scheduled workflow refreshes it (scripts/fetch_profile.py).
   ========================================================================== */

(() => {
  "use strict";

  const SNAPSHOT = window.PROFILE;

  if (!SNAPSHOT) {
    console.warn("profile data missing — run: python3 scripts/fetch_profile.py");
    return;
  }

  const API = "https://api.github.com";
  const LIVE = true; // false → always render the committed snapshot
  const CACHE_KEY = "github-profile:live";
  const CACHE_TTL = 10 * 60 * 1000; // don't hammer the 60-req/hr anonymous limit
  const MAX_LANGUAGE_REPOS = 8;
  const MAX_PROJECTS = 8; // mirrors the fetch script's cap

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

  function dayLong(value) {
    const date = typeof value === "string" ? new Date(value) : value;
    return date.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    });
  }

  const host = (name) => document.querySelector('[data-render="' + name + '"]');

  /* ------------------------------------------------------------- paints -- */

  const STAT_LABELS = [
    ["repos", "Total repos"],
    ["stars", "All stars"],
    ["followers", "Followers"],
    ["years_active", "Years active"],
  ];

  function paintStats(state) {
    const target = host("stats");
    if (!target) return;
    target.replaceChildren();
    for (const [key, label] of STAT_LABELS) {
      target.appendChild(
        el("div", { class: "stat" }, [
          el("span", { class: "stat__value", text: compact(state.stats[key]) }),
          el("span", { class: "stat__label", text: label }),
        ])
      );
    }
  }

  function paintProfile(state) {
    const target = host("profile");
    if (!target) return;
    target.replaceChildren();

    const user = state.user;
    const rows = [];

    if (user.company) {
      rows.push(
        el("div", { class: "profile__row" }, [icon(ICON.building), el("span", { text: user.company })])
      );
    }
    if (user.location) {
      rows.push(
        el("div", { class: "profile__row" }, [icon(ICON.location), el("span", { text: user.location })])
      );
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

    target.appendChild(
      el("img", {
        class: "profile__avatar",
        src: user.avatar,
        alt: user.name,
        width: "88",
        height: "88",
        loading: "lazy",
      })
    );
    target.appendChild(el("h2", { class: "profile__name", text: user.name }));
    target.appendChild(el("p", { class: "profile__handle", text: "@" + user.login }));
    if (user.bio) {
      target.appendChild(el("p", { class: "profile__bio", text: user.bio }));
    }
    target.appendChild(
      el("div", { class: "profile__actions" }, [
        el("a", {
          class: "btn btn--primary",
          href: user.profile_url,
          rel: "me",
          text: "Follow on GitHub",
        }),
      ])
    );
    target.appendChild(el("div", { class: "profile__rows" }, rows));
  }

  function paintTech(state) {
    const target = host("tech");
    if (!target) return;
    target.replaceChildren();

    target.appendChild(
      el("div", { class: "panel__head" }, [
        el("h2", { class: "panel__title", text: "Tech Stack & Languages" }),
        el("span", { class: "panel__meta", text: "By bytes committed" }),
      ])
    );

    const chips = el("ul", { class: "chips" });
    for (const tech of state.core_tech) {
      chips.appendChild(el("li", { class: "chip", text: tech }));
    }

    const bars = el("div", { class: "bars" });
    for (const language of state.languages) {
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

    target.appendChild(el("p", { class: "tech__label", text: "Core technologies" }));
    target.appendChild(chips);
    target.appendChild(el("p", { class: "tech__label", text: "Languages" }));
    target.appendChild(bars);
  }

  function paintContributions(state) {
    const target = host("contributions");
    if (!target) return;
    target.replaceChildren();

    const contrib = state.contributions;
    if (!contrib) return;

    const start = utcDate(contrib.start);
    const lead = start.getUTCDay(); // 0 = Sunday
    const columns = Math.ceil((lead + contrib.days) / 7);
    const levels = contrib.levels.split("");

    target.appendChild(
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

    target.appendChild(el("div", { class: "heat__scroll" }, [months, grid]));
    target.appendChild(legend);
  }

  function paintProjects(state) {
    const target = host("projects");
    if (!target) return;
    target.replaceChildren();

    target.appendChild(
      el("div", { class: "projects__head" }, [
        el("h2", { class: "panel__title", text: "Notable Projects" }),
        el("span", { class: "panel__meta", text: "Most stars" }),
      ])
    );

    const grid = el("div", { class: "projects__grid" });
    for (const project of state.projects) {
      const foot = el("div", { class: "project__foot" });
      if (project.language) {
        foot.appendChild(
          el("span", { class: "project__stat" }, [
            el("span", { class: "lang-dot" }),
            el("span", { text: project.language }),
          ])
        );
      }
      const counters = [
        [ICON.star, project.stars, "stars"],
        [ICON.fork, project.forks, "forks"],
        [ICON.issue, project.issues, "open issues"],
      ];
      for (const [markup, value, label] of counters) {
        foot.appendChild(
          el("span", { class: "project__stat", title: compact(value) + " " + label }, [
            icon(markup),
            el("span", { text: compact(value) }),
          ])
        );
      }
      if (project.homepage) {
        foot.appendChild(
          el("span", { class: "project__stat" }, [
            el("a", { href: project.homepage, title: "Live site", text: "Live" }),
            icon(ICON.link),
          ])
        );
      }

      grid.appendChild(
        el("div", { class: "project" }, [
          el("h3", { class: "project__name" }, [el("a", { href: project.url, text: project.name })]),
          el("p", {
            class: "project__desc",
            text: project.description || "No description yet.",
          }),
          foot,
        ])
      );
    }

    target.appendChild(grid);
  }

  function paint(state) {
    for (const node of document.querySelectorAll("[data-fill]")) {
      if (node.dataset.fill === "name") node.textContent = state.user.name;
      if (node.dataset.fill === "handle") node.textContent = "@" + state.user.login;
      if (node.dataset.fill === "generated") {
        node.textContent = dayLong(state.generated);
        node.setAttribute("datetime", state.generated);
      }
    }

    paintStats(state);
    paintProfile(state);
    paintTech(state);
    paintContributions(state);
    paintProjects(state);
  }

  function setSource(state) {
    const node = document.querySelector('[data-fill="source"]');
    if (!node) return;
    if (state === "live") node.textContent = "Numbers are live from GitHub’s public API.";
    if (state === "snapshot") {
      node.textContent =
        "Numbers come from the committed snapshot — GitHub’s API was out of reach.";
    }
  }

  /* --------------------------------------------------------- live data --- */

  const cache = {
    read() {
      try {
        const raw = window.localStorage.getItem(CACHE_KEY);
        if (!raw) return null;
        const entry = JSON.parse(raw);
        return Date.now() - entry.at < CACHE_TTL ? entry.data : null;
      } catch (error) {
        return null;
      }
    },
    write(data) {
      try {
        window.localStorage.setItem(CACHE_KEY, JSON.stringify({ at: Date.now(), data }));
      } catch (error) {
        /* private mode or quota — caching is optional */
      }
    },
  };

  async function api(path, accept = "application/vnd.github+json") {
    const response = await fetch(API + path, { headers: { Accept: accept } });
    if (!response.ok) throw new Error("GitHub API " + response.status + " for " + path);
    return response.json();
  }

  function yearsActive(createdAt) {
    const created = utcDate(createdAt.slice(0, 10));
    const today = new Date();
    const thisYear = new Date(
      Date.UTC(today.getUTCFullYear(), created.getUTCMonth(), created.getUTCDate())
    );
    return Math.max(1, today.getUTCFullYear() - created.getUTCFullYear() - (today < thisYear ? 1 : 0));
  }

  /** Fetch profile + repos, and per-repo language bytes, then reshape to the
      same object the snapshot uses. */
  async function fetchLive(login, snapshot) {
    const [profile, repos] = await Promise.all([
      api("/users/" + login),
      api("/users/" + login + "/repos?per_page=100&sort=pushed"),
    ]);

    const own = repos.filter((repo) => !repo.fork);
    const largest = own.slice().sort((a, b) => b.size - a.size).slice(0, MAX_LANGUAGE_REPOS);

    const byteCounts = {};
    const languageLists = await Promise.all(
      largest.map((repo) =>
        api("/repos/" + login + "/" + repo.name + "/languages").catch(() => ({}))
      )
    );
    for (const list of languageLists) {
      for (const [name, bytes] of Object.entries(list)) {
        byteCounts[name] = (byteCounts[name] || 0) + bytes;
      }
    }

    const totalBytes = Object.values(byteCounts).reduce((sum, bytes) => sum + bytes, 0) || 1;
    const languages = Object.entries(byteCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([name, bytes]) => ({ name, pct: Math.round((bytes * 1000) / totalBytes) / 10 }));

    const descriptions = new Map(snapshot.projects.map((p) => [p.name, p.description]));
    const projects = own
      .map((repo) => ({
        name: repo.name,
        url: repo.html_url,
        description: repo.description || descriptions.get(repo.name) || "",
        language: repo.language || "",
        stars: repo.stargazers_count,
        forks: repo.forks_count,
        issues: repo.open_issues_count,
        homepage: repo.homepage || "",
        pushed_at: repo.pushed_at,
      }))
      .sort((a, b) => b.stars - a.stars || a.name.localeCompare(b.name))
      .slice(0, MAX_PROJECTS);

    return {
      ...snapshot,
      user: {
        ...snapshot.user,
        login: profile.login,
        name: profile.name || profile.login,
        bio: profile.bio || "",
        company: profile.company || snapshot.user.company,
        location: profile.location || "",
        blog: profile.blog || "",
        profile_url: profile.html_url,
        joined: profile.created_at.slice(0, 10),
        followers: profile.followers,
        following: profile.following,
        // the avatar stays the locally committed copy — no third-party request
      },
      stats: {
        repos: own.length,
        stars: own.reduce((sum, repo) => sum + repo.stargazers_count, 0),
        followers: profile.followers,
        years_active: yearsActive(profile.created_at),
      },
      languages,
      projects,
    };
  }

  /* -------------------------------------------------------------- boot --- */

  paint(SNAPSHOT);

  if (!LIVE || !window.fetch) {
    setSource("snapshot");
    return;
  }

  (async () => {
    const login = SNAPSHOT.user.login;
    try {
      let live = cache.read();
      if (!live) {
        live = await fetchLive(login, SNAPSHOT);
        cache.write(live);
      }
      paint(live);
      setSource("live");
    } catch (error) {
      console.warn("live GitHub data unavailable, showing the snapshot:", error.message);
      setSource("snapshot");
    }
  })();
})();
