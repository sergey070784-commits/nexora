(() => {
  "use strict";

  // Python Admin will implement these two endpoints.
  const API = {
    login: "/api/admin/login"
  };
  const SESSION_KEY = "nexora_admin_session";
  const $ = (selector, root=document) => root.querySelector(selector);
  const $$ = (selector, root=document) => Array.from(root.querySelectorAll(selector));
  let active = null;
  let pendingImageFile = null;
  let currentImageUrl = "";
  let adminSession = null;

  function showStatus(message, isError=false) {
    const el = $("#adminStatus");
    if (!el) return;
    el.textContent = message;
    el.classList.toggle("error", !!isError);
    el.classList.add("show");
    window.clearTimeout(showStatus.timer);
    showStatus.timer = window.setTimeout(() => el.classList.remove("show"), 5000);
  }
  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
  }
  function setText(selector, value) {
    const el = $(selector);
    if (el && value !== undefined && value !== null && value !== "") el.textContent = String(value);
  }
  function setButtonText(el, value) {
    if (!el || value === undefined || value === null) return;
    const arrow = el.querySelector("span");
    el.textContent = String(value);
    if (arrow) el.appendChild(arrow);
  }
  function setHeading(selector, value) {
    const el = $(selector);
    if (!el || value === undefined || value === null || value === "") return;
    const parts = String(value).split("\n", 2);
    if (parts[1]) {
      const em = document.createElement("em"); em.textContent = parts[1];
      el.replaceChildren(document.createTextNode(parts[0]), document.createElement("br"), em);
    } else el.textContent = parts[0];
  }
  function normaliseSite(raw) {
    const s = raw || {};
    const getService = (n, part) => {
      const nested = s[`service_${n}`];
      return (nested && typeof nested === "object" ? nested[part] : undefined)
        ?? s[`service_${n}_${part}`] ?? "";
    };
    return {
      name:s.name, profession:s.profession, headline:s.headline, hero_text:s.hero_text, cta:s.cta,
      experience:s.experience, experience_text:s.experience_text,
      section_about:s.section_about, about_heading:s.about_heading, about_text_1:s.about_text_1, about_text_2:s.about_text_2,
      section_services:s.section_services, services_heading:s.services_heading,
      service_1:{title:getService(1,"title"),description:getService(1,"description")},
      service_2:{title:getService(2,"title"),description:getService(2,"description")},
      service_3:{title:getService(3,"title"),description:getService(3,"description")},
      quote:s.quote, section_contact:s.section_contact, contact_heading:s.contact_heading,
      contact_cta:s.contact_cta, phone:s.phone, email:s.email, location:s.location
    };
  }
  function applySiteData(rawSite, imageUrl) {
    const site = normaliseSite(rawSite);
    if (site.name) {
      const brand = $(".brand");
      if (brand) {
        const parts = String(site.name).trim().split(/\s+/);
        const first = parts.shift() || ""; const last = parts.join(" ");
        const span = document.createElement("span"); span.textContent = last;
        brand.replaceChildren(document.createTextNode(first + (last ? " " : "")), span);
      }
      setText("footer span:first-child", `${site.name} — ${site.profession || ""}`);
    }
    setText(".eyebrow",site.profession); setHeading(".heading-edit",site.headline); setText(".hero-text",site.hero_text);
    setButtonText($(".hero-copy .primary-cta"),site.cta);
    setText(".experience strong",site.experience === undefined ? "" : `${String(site.experience).replace(/\+$/,'')}+`);
    setText(".experience span",site.experience_text);
    const portrait=$(".portrait");
    if (portrait && imageUrl) {
      portrait.querySelector("img")?.remove();
      const img=document.createElement("img"); img.src=imageUrl; img.alt=site.name ? `${site.name} — portrait` : "Portrait";
      img.onerror=()=>{img.remove();portrait.classList.remove("has-image");};
      portrait.classList.add("has-image"); portrait.appendChild(img);
      currentImageUrl=imageUrl;
    }
    setText("#about .section-name",site.section_about); setText('.nav-link[data-nav-key="about"]',site.section_about);
    setHeading("#about .section-heading",site.about_heading);
    const about=$$("#about .about-text"); if(about[0] && site.about_text_1) about[0].textContent=site.about_text_1; if(about[1] && site.about_text_2) about[1].textContent=site.about_text_2;
    setText("#services .section-name",site.section_services); setText('.nav-link[data-nav-key="services"]',site.section_services);
    setHeading("#services .section-heading",site.services_heading);
    [site.service_1,site.service_2,site.service_3].forEach((v,i)=>{const card=$$(".service-card")[i]; if(!card||!v)return; if(v.title) card.querySelector("h3").textContent=v.title; if(v.description) card.querySelector("p").textContent=v.description;});
    setText(".quote",site.quote);
    setText("#contact .section-name",site.section_contact); setText('.nav-link[data-nav-key="contact"]',site.section_contact);
    setHeading("#contact .section-heading",site.contact_heading); setButtonText($(".contact-cta"),site.contact_cta);
    const contacts=$$(".contact-item"); [site.phone,site.email,site.location].forEach((v,i)=>{if(contacts[i]&&v)contacts[i].textContent=v;});
  }
  function readSiteData() {
    const text = sel => $(sel)?.innerText.replace(/\u00a0/g," ").trim() || "";
    const rich = sel => { const el=$(sel); if(!el)return ""; let out=""; el.childNodes.forEach(n=>{if(n.nodeName==="BR")out+="\n"; else if(n.nodeType===Node.TEXT_NODE)out+=n.textContent; else if(n.nodeType===Node.ELEMENT_NODE)out+=n.textContent;}); return out.trim(); };
    const services=$$(".service-card");
    return {
      name:text(".brand"), profession:text(".eyebrow"), headline:rich(".heading-edit"), hero_text:text(".hero-text"), cta:text(".hero-copy .primary-cta").replace(/↗/g,"").trim(),
      experience:text(".experience strong").replace(/\+$/,""), experience_text:text(".experience span"),
      section_about:text("#about .section-name"), about_heading:rich("#about .section-heading"), about_text_1:textAll("#about .about-text",0), about_text_2:textAll("#about .about-text",1),
      section_services:text("#services .section-name"), services_heading:rich("#services .section-heading"),
      service_1:{title:services[0]?.querySelector("h3")?.textContent.trim()||"",description:services[0]?.querySelector("p")?.textContent.trim()||""},
      service_2:{title:services[1]?.querySelector("h3")?.textContent.trim()||"",description:services[1]?.querySelector("p")?.textContent.trim()||""},
      service_3:{title:services[2]?.querySelector("h3")?.textContent.trim()||"",description:services[2]?.querySelector("p")?.textContent.trim()||""},
      quote:text(".quote"), section_contact:text("#contact .section-name"), contact_heading:rich("#contact .section-heading"), contact_cta:text(".contact-cta").replace(/↗/g,"").trim(),
      phone:text(".contact-item:nth-child(1)"), email:text(".contact-item:nth-child(2)"), location:text(".contact-item:nth-child(3)")
    };
    function textAll(sel,i){return $$(sel)[i]?.innerText.trim()||"";}
  }
  function openEditor(element) {
    active=element;
    const overlay=$("#editorOverlay"), body=$("#editorBody");
    $("#editorTitle").textContent=element.dataset.label||"Edit element"; body.innerHTML="";
    const type=element.dataset.edit;
    if(type==="section-name") {
      const current=element.querySelector(".section-name")?.textContent||"";
      body.innerHTML=`<label class="editor-label" for="editorInput">Section name</label><input class="editor-input" id="editorInput" maxlength="40" value="${escapeHtml(current)}"><p class="editor-description">This name updates both the section label and the matching top navigation item.</p>`;
    } else if(type==="image") {
      body.innerHTML=`<p class="editor-description">Choose a new photo. It will be uploaded when you save all changes.</p><button type="button" class="upload-button" id="chooseImage">Choose photo</button><div class="image-preview" id="imagePreview">${element.querySelector("img")?`<img src="${escapeHtml(element.querySelector("img").src)}" alt="Current photo">`:'<span>No photo selected</span>'}</div>`;
      $("#chooseImage").onclick=()=>$("#imageInput").click();
      $("#imageInput").onchange=()=>{const file=$("#imageInput").files?.[0];if(!file)return;pendingImageFile=file;const reader=new FileReader();reader.onload=()=>{$("#imagePreview").innerHTML=`<img src="${reader.result}" alt="Selected photo">`;};reader.readAsDataURL(file);};
    } else if(type==="experience-label") {
      body.innerHTML=`<label class="editor-label" for="editorInput">Experience label</label><textarea class="editor-textarea" id="editorInput" maxlength="80">${escapeHtml(element.querySelector("span")?.innerText||"")}</textarea>`;
    } else if(type==="experience-number") {
      body.innerHTML=`<label class="editor-label" for="editorInput">Experience number</label><input class="editor-input" id="editorInput" type="number" min="0" max="99" value="${escapeHtml(element.querySelector("strong")?.textContent.replace("+","")||"")}">`;
    } else if(type==="service") {
      body.innerHTML=`<label class="editor-label" for="serviceTitle">Service name</label><input class="editor-input" id="serviceTitle" maxlength="60" value="${escapeHtml(element.querySelector("h3")?.textContent||"")}"><label class="editor-label" for="serviceDescription">Description</label><textarea class="editor-textarea" id="serviceDescription" maxlength="180">${escapeHtml(element.querySelector("p")?.textContent||"")}</textarea>`;
    } else {
      const current=element.innerText.replace("↗","").trim(); const isArea=type==="textarea";
      body.innerHTML=`<label class="editor-label" for="editorInput">${escapeHtml(element.dataset.label||"Text")}</label>${isArea?`<textarea class="editor-textarea" id="editorInput">${escapeHtml(current)}</textarea>`:`<input class="editor-input" id="editorInput" type="text" value="${escapeHtml(current)}">`}`;
    }
    overlay.hidden=false; document.body.classList.add("editing"); body.querySelector("input,textarea,button")?.focus();
  }
  function closeEditor(){$("#editorOverlay").hidden=true;document.body.classList.remove("editing");active=null;pendingImageFile=null;$("#imageInput").value="";}
  function applyChanges(){
    if(!active)return; const type=active.dataset.edit;
    if(type==="section-name") {const value=$("#editorInput").value.trim();if(!value)return;const section=active.dataset.section;active.querySelector(".section-name").textContent=value;const nav=$(`[data-nav-key="${section}"]`);if(nav)nav.textContent=value;}
    else if(type==="image"){const preview=$("#imagePreview img");if(preview){active.querySelector("img")?.remove();const img=document.createElement("img");img.src=preview.src;img.alt="Portrait";active.appendChild(img);active.classList.add("has-image");}}
    else if(type==="experience-number"){const v=Math.max(0,Math.min(99,Number($("#editorInput").value)||0));active.querySelector("strong").textContent=v+"+";}
    else if(type==="experience-label"){const v=$("#editorInput").value.trim();if(!v)return;active.querySelector("span").innerHTML=escapeHtml(v).replace(/\r?\n/g,"<br>");}
    else if(type==="service"){active.querySelector("h3").textContent=$("#serviceTitle").value.trim()||"Service";active.querySelector("p").textContent=$("#serviceDescription").value.trim();}
    else {const v=$("#editorInput").value.trim();if(!v)return;const key=active.dataset.key;if(key==="name"){const p=v.split(/\s+/);const first=p.shift()||"";const span=document.createElement("span");span.textContent=p.join(" ");active.replaceChildren(document.createTextNode(first+(p.length?" ":"")),span);}else if(["headline","about_heading","services_heading","contact_heading"].includes(key)){const parts=v.split(/\s+/);const breakAt=Math.max(1,Math.floor(parts.length/2));const em=document.createElement("em");em.textContent=parts.slice(breakAt).join(" ");active.replaceChildren(document.createTextNode(parts.slice(0,breakAt).join(" ")),document.createElement("br"),em);}else if(["cta","contact_cta"].includes(key)){const span=document.createElement("span");span.textContent="↗";active.replaceChildren(document.createTextNode(v+" "),span);}else active.textContent=v;}
    closeEditor();
  }
  function bindEditor(){
    $$(".editable").forEach(el=>{el.addEventListener("click",e=>{e.preventDefault();openEditor(el);});el.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();openEditor(el);}});});
    $("#editorSave").addEventListener("click",applyChanges);$("#editorClose").addEventListener("click",closeEditor);$("#editorCancel").addEventListener("click",closeEditor);
    $("#editorOverlay").addEventListener("click",e=>{if(e.target===$("#editorOverlay"))closeEditor();});
    document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!$("#editorOverlay").hidden)closeEditor();});
  }
  function saveAll(){
    // Deliberately local-only in this stage. OTP verification and the real
    // persistence request will be connected before enabling server-side save.
    showStatus("השמירה תופעל לאחר אימות קוד. השינויים כרגע נשארים בדפדפן בלבד.");
  }
  function initEditor(){
    try{adminSession=JSON.parse(sessionStorage.getItem(SESSION_KEY)||"null");}catch{}
    if(!adminSession?.slot_id||!adminSession?.site){showStatus("לא נמצאה התחברות. נא להיכנס מחדש.",true);setTimeout(()=>location.replace("index.html"),1200);return;}
    applySiteData(adminSession.site,adminSession.image||"");
    bindEditor();$("#adminSaveButton").addEventListener("click",saveAll);
    console.log("Nexora Admin editor ready for slot",adminSession.slot_id);
  }
  if(location.pathname.endsWith("editor.html"))document.addEventListener("DOMContentLoaded",initEditor);
})();
