import asyncio,sys,time
from playwright.async_api import async_playwright
U=sys.argv[1] if len(sys.argv)>1 else 'https://tommyliu2009.github.io/subsidy-news/'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=await b.new_page(viewport={'width':1366,'height':900})
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(U+'?t='+str(int(time.time())),wait_until='networkidle')
    print('title',await pg.title());print('cards',await pg.locator('.card').count(),'side ad',await pg.locator('.side .ad').first.is_visible(),'open',await pg.locator('.olist li').count())
    print('補助王 links',await pg.locator('a[href="https://www.subsidyking.tw/"]').count())
    for c in ['補助政策','補助成果發表','補助資訊']:
      await pg.click(f'#tabs button[data-c="{c}"]');print(c,await pg.inner_text('#cmeta'))
    await pg.click('#tabs button[data-c="首頁"]')
    # 訂閱表單測試（攔截 mailto，不實際寄信）
    await pg.evaluate("window._u=null;Object.defineProperty(window,'location',{value:{...location,set href(v){window._u=v}}})") if False else None
    reqs=[];pg.on('framenavigated',lambda f:reqs.append(f.url))
    await pg.fill('#semail','test-delete-me@example.com');await pg.uncheck('#subf input[value="補助成果發表"]')
    await pg.route('mailto:*',lambda r:r.abort())
    await pg.click('#subf button');await pg.wait_for_timeout(800)
    print('subscribe msg visible',await pg.locator('#smsg').is_visible(),(await pg.inner_text('#smsg'))[:40])
    await pg.screenshot(path='shot.png')
    m=await b.new_page(viewport={'width':390,'height':844},is_mobile=True,device_scale_factor=2);await m.goto(U,wait_until='networkidle')
    print('mobile ad visible',await m.locator('.mad').is_visible());await m.screenshot(path='shot_mobile.png')
    print('errors',errs);await b.close()
asyncio.run(main())
