const dates = document.getElementsByClassName('date');
const header = document.getElementById('header');
const nav = document.getElementById('nav');
const logo = document.getElementById('logo');


// CONVERT epoch dates to date strings
for (const d of dates) {
    const opt = { dateStyle: "medium" };
    dt = parseInt(d.innerHTML);
    dt = new Date(dt * 1000);
    d.innerHTML = dt.toLocaleString('fr-FR', opt );
}


// The Header Scroll effect
window.addEventListener("scroll", (event) => {
    let scpos = this.scrollY;
    if (scpos > 100) {
        header.style.fontSize = '.9em';
        nav.style.padding     = '.3em 0';
        logo.style.display    = 'none';
    } else {
        header.style.fontSize = null;
        nav.style.padding     = null;
        logo.style.display    = null;
    }
});