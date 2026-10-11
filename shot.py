import asyncio,sys,time
from playwright.async_api import async_playwright
U=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8765/'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=await b.new_page(viewport={'width':1366,'height':900})
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(U+'?t='+str(int(time.time())),wait_until='networkidle')
    print('lead:',(await pg.inner_text('#lead h2'))[:60]);print('cards',await pg.locator('.card').count(),'side ad',await pg.locator('.side .ad').first.is_visible())
    for c in ['台灣產業','全球AI','全球產業趨勢','政策與補助']:
      await pg.click(f'#tabs button[data-c="{c}"]');print(c,await pg.inner_text('#cmeta'),'|',(await pg.inner_text('#topics'))[:120].replace('\n',' '))
    await pg.click('#tabs button[data-c="首頁"]');await pg.screenshot(path='shot.png')
    m=await b.new_page(viewport={'width':390,'height':844},is_mobile=True,device_scale_factor=2);await m.goto(U,wait_until='networkidle')
    print('mobile ad visible',await m.locator('.mad').is_visible());await m.screenshot(path='shot_mobile.png')
    print('errors',errs);await b.close()
asyncio.run(main())
