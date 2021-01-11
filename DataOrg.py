import json


def JsonPacker():
    with open('Data.json','r') as f:
        data = json.load(f)

        MainNames = []
        MainUrls = []
        MainData = {}

        for msg in data[::-1]:
            try:
                TempNames = []
                TempUrls = []

                if not msg['id'] in [66,65,3]:
                    if msg['id'] == 63:
                        names = msg['message'].split('\n\n')
                        names = names[1].split('\n')
                    else:
                        names = msg['message'].split('\n')[1:]
                    for name in names:
                        MainNames.append(name)
                        TempNames.append(name)


                    for url in msg['entities']:
                        if url['_'] == 'MessageEntityTextUrl':
                            if url['offset'] == 67 and url['url'] == 'https://t.me/anime_flix_pro/467':
                                continue
                            else:
                                MainUrls.append(url['url'])
                                TempUrls.append(url['url'])

            except Exception as e:
                print(e,msg['id'])

            else:
                MainData.update(dict(zip(TempNames,TempUrls)))

        with open('urls.json','w') as f:
            json.dump(MainData,f,indent=4)

