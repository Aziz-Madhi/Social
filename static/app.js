const state = {
  images: { hooks: [], slides: [], demos: [] },
};

const el = (id) => document.getElementById(id);

function getFontAxes() {
  return {
    opsz: Number(el("opsz").value),
    wdth: Number(el("wdth").value),
    wght: Number(el("wght").value),
    slnt: Number(el("slnt").value),
  };
}

function getSizes() {
  return {
    cover_title: Number(el("coverTitleSize").value),
    cover_subtitle: Number(el("coverSubtitleSize").value),
    content: Number(el("contentSize").value),
  };
}

function applyRandomToggles() {
  const hookSelect = el("hookImage");
  const slideSelect = el("slideImages");
  const demoSelect = el("demoImage");

  hookSelect.disabled = el("randomHooks").checked;
  slideSelect.disabled = el("randomSlides").checked;
  demoSelect.disabled = el("randomDemos").checked;
}

function populateSelect(select, options) {
  select.innerHTML = "";
  for (const item of options) {
    const opt = document.createElement("option");
    opt.value = item;
    opt.textContent = item;
    select.appendChild(opt);
  }
}

function renderShows(count, slidesPerShow) {
  const container = el("shows");
  container.innerHTML = "";

  for (let showIndex = 1; showIndex <= count; showIndex += 1) {
    const wrapper = document.createElement("div");
    wrapper.className = "show-item";
    wrapper.dataset.showIndex = String(showIndex);

    const heading = document.createElement("h3");
    heading.textContent = `Slideshow ${showIndex}`;
    wrapper.appendChild(heading);

    for (let slideIndex = 1; slideIndex <= slidesPerShow; slideIndex += 1) {
      const slideBlock = document.createElement("div");
      slideBlock.className = "slide-block";
      slideBlock.dataset.slideIndex = String(slideIndex);

      const title = document.createElement("h4");
      title.textContent = slideIndex === 1 ? "Cover Slide" : `Slide ${slideIndex}`;
      slideBlock.appendChild(title);

      const grid = document.createElement("div");
      grid.className = "grid";

      const titleLabel = document.createElement("label");
      titleLabel.textContent = "Title";
      const titleInput = document.createElement("input");
      titleInput.type = "text";
      titleInput.dataset.field = "title";
      titleLabel.appendChild(titleInput);

      grid.appendChild(titleLabel);

      if (slideIndex === 1) {
        const subtitleLabel = document.createElement("label");
        subtitleLabel.textContent = "Subtitle";
        const subtitleInput = document.createElement("input");
        subtitleInput.type = "text";
        subtitleInput.dataset.field = "subtitle";
        subtitleLabel.appendChild(subtitleInput);
        grid.appendChild(subtitleLabel);
      } else {
        const bodyLabel = document.createElement("label");
        bodyLabel.textContent = "Body";
        const bodyInput = document.createElement("textarea");
        bodyInput.dataset.field = "body";
        bodyLabel.appendChild(bodyInput);
        grid.appendChild(bodyLabel);

        const realityLabel = document.createElement("label");
        realityLabel.textContent = "Reality";
        const realityInput = document.createElement("textarea");
        realityInput.dataset.field = "reality";
        realityLabel.appendChild(realityInput);
        grid.appendChild(realityLabel);
      }

      slideBlock.appendChild(grid);
      wrapper.appendChild(slideBlock);
    }

    container.appendChild(wrapper);
  }
}

async function loadImages() {
  const res = await fetch("/api/images");
  state.images = await res.json();
  populateSelect(el("hookImage"), state.images.hooks);
  populateSelect(el("slideImages"), state.images.slides);
  populateSelect(el("demoImage"), state.images.demos);

  const previewFolder = el("previewFolder").value;
  populateSelect(el("previewImage"), state.images[previewFolder]);
}

function collectShows() {
  const showBlocks = [...document.querySelectorAll(".show-item")];
  return showBlocks.map((block) => {
    const slides = [];
    const slideBlocks = [...block.querySelectorAll(".slide-block")];

    slideBlocks.forEach((slideBlock, index) => {
      const titleInput = slideBlock.querySelector('[data-field="title"]');
      const subtitleInput = slideBlock.querySelector('[data-field="subtitle"]');
      const bodyInput = slideBlock.querySelector('[data-field="body"]');
      const realityInput = slideBlock.querySelector('[data-field="reality"]');

      if (index === 0) {
        slides.push({
          type: "cover",
          texts: {
            title: titleInput?.value || "",
            subtitle: subtitleInput?.value || "",
          },
        });
      } else {
        slides.push({
          type: "content",
          texts: {
            title: titleInput?.value || "",
            body: bodyInput?.value || "",
            reality: realityInput?.value || "",
          },
        });
      }
    });

    return { slides };
  });
}

async function runPreview() {
  const status = el("previewStatus");
  status.textContent = "";

  const folder = el("previewFolder").value;
  const imagePath = el("previewImage").value;
  const slideType = el("previewSlideType").value;

  const payload = {
    folder,
    imagePath: imagePath || null,
    slideType,
    aspectRatio: el("aspectRatio").value,
    fontAxes: getFontAxes(),
    sizes: getSizes(),
    texts: {
      title: el("previewTitle").value,
      subtitle: el("previewSubtitle").value,
      body: el("previewBody").value,
      reality: el("previewReality").value,
    },
  };

  try {
    const res = await fetch("/api/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      status.textContent = data.error || "Preview failed";
      return;
    }
    el("previewImageTag").src = data.dataUrl;
  } catch (err) {
    status.textContent = String(err);
  }
}

async function saveBatch() {
  const status = el("saveStatus");
  status.textContent = "Saving...";

  const payload = {
    shows: collectShows(),
    options: {
      aspectRatio: el("aspectRatio").value,
      fontAxes: getFontAxes(),
      sizes: getSizes(),
      useDemoImageForLast: el("useDemoImageForLast").checked,
    },
    images: {
      randomHooks: el("randomHooks").checked,
      randomSlides: el("randomSlides").checked,
      randomDemos: el("randomDemos").checked,
      hookImage: el("hookImage").value,
      slideImages: [...el("slideImages").selectedOptions].map((opt) => opt.value),
      demoImage: el("demoImage").value,
    },
  };

  try {
    const res = await fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      status.textContent = data.error || "Save failed";
      return;
    }
    status.textContent = `Saved ${data.saved.length} slideshows to ready_to_post/`;
  } catch (err) {
    status.textContent = String(err);
  }
}

el("applyCount").addEventListener("click", () => {
  const count = Number(el("showCount").value || 1);
  const slidesPerShow = Number(el("slidesPerShow").value || 5);
  renderShows(count, slidesPerShow);
});

el("randomHooks").addEventListener("change", applyRandomToggles);
el("randomSlides").addEventListener("change", applyRandomToggles);
el("randomDemos").addEventListener("change", applyRandomToggles);

el("previewFolder").addEventListener("change", () => {
  const folder = el("previewFolder").value;
  populateSelect(el("previewImage"), state.images[folder] || []);
});

el("runPreview").addEventListener("click", runPreview);
el("saveBatch").addEventListener("click", saveBatch);

renderShows(1, 5);
applyRandomToggles();
loadImages();
