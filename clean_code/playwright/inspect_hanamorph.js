const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('https://hanamorph3.cfapps.eu30.hana.ondemand.com/', { waitUntil: 'networkidle', timeout: 45000 });
  await page.waitForTimeout(2000);
  await page.getByText('CDS View Migration').first().click();
  await page.waitForTimeout(2500);

  const inner = await page.evaluate(() => ({
    url: window.location.href,
    inputs: Array.from(document.querySelectorAll('input, select, textarea')).map((el) => ({
      tag: el.tagName,
      type: el.type,
      placeholder: el.placeholder,
      cls: el.className.toString().slice(0, 60),
    })),
    buttons: Array.from(document.querySelectorAll('button, [role="button"]')).map((el) => el.innerText.trim()).filter(Boolean).slice(0, 25),
    steps: Array.from(document.querySelectorAll('[class*="Wizard"], [class*="Step"], [class*="wizard"], [class*="step"]')).map((el) => ({
      cls: el.className.toString().slice(0, 80),
      text: el.innerText.trim().slice(0, 120),
    })).slice(0, 15),
    text: document.body.innerText.slice(0, 2500),
  }));

  console.log(JSON.stringify(inner, null, 2));
  await browser.close();
})();
