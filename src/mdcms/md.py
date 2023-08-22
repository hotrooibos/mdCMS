import logging
import os
import unicodedata
from time import time

from markdown import Markdown

from . import constants as const
from . import utils

# Init logger
log = logging.getLogger(__name__)



class Md:
    """Markdown document class.
    File name and URL strings to .md file in argument.
    
    Usage:
        mdfile = Md('readme.md', '/home/antoine/readme.md')
    """
    urls = []

    def __init__(self, f_name: str, f_url: str):
        # Read .md file and make attributes from its content
        with open(file=f_url,
                  mode='r',
                  encoding='utf-8') as mdf:
            mddat = mdf.read()

        # Datas to write to .md
        wmd = []
        md = Markdown(extensions=['meta','toc','extra',
                                  'codehilite','md_in_html'])

        self.f_url = f_url
        self.content = md.convert(mddat)
        self.toc = md.toc
        self.m_time = os.stat(self.f_url).st_mtime

        #
        # Metas
        #
        self.f_name = f_name
        self.title = f_name[:-3]
        self.author = const.DEFAULT_AUTHOR
        self.url = None
        self.urlredir = []
        self.ctime = None
        self.cyear = None
        self.lang = const.DEFAULT_LANG
        self.langflag = None
        self.originpost = None
        self.cat = None
        self.preview = None

        #
        # TITLE : get or use+write the one from filename
        #
        if md.Meta.get('title'):
            self.title = md.Meta.get('title')[0]
        else:
            wmd.append(('title', self.title))
            log.warning(f"{f_name}: no title specified.")

        #
        # PERMA URL : get or build it
        #
        if md.Meta.get('url'):
            self.url = md.Meta.get('url')[0]        
        else:
            self.url = self.build_url()

        if self.url not in Md.urls:
            Md.urls.append(self.url)
        else:
            log.warning(f"Error in {f_name} : url for {self.url} already exists, changing url.")
            self.url = self.build_url()


        #
        # REDIRECTION URLs
        #
        if md.Meta.get('urlredir'):
            for url in md.Meta.get('urlredir'):
                self.urlredir.append(url)

                if url not in Md.urls:
                    # log.info(f'{f_name}: add "{url}" redirection')
                    Md.urls.append(url)

        #
        # AUTHOR : get from md or consts
        #
        if md.Meta.get('author'):
            self.author = md.Meta.get('author')[0]
        else:
            self.author = const.DEFAULT_AUTHOR

        #
        # LANGUAGE : get from md or consts
        # ORIGINPOST : get from md if lang != default lang
        #
        if md.Meta.get('lang'):
            self.lang = (md.Meta.get('lang')[0])[:2]

            # Get original/translated post if post lang
            # is different from the default CMS writing
            # language (const.DEFAULT_LANG)
            if self.lang != const.DEFAULT_LANG[:2]:
                if md.Meta.get('originpost'):
                    self.originpost = md.Meta.get('originpost')[0]
                else:
                    self.title = f'[{self.lang}] {self.title}'
        else:
            self.lang = const.DEFAULT_LANG[:2]

        #
        # CATEGORIES : get from md
        #
        if md.Meta.get('categories'):
            self.cat = md.Meta.get('categories')
        else:
            self.cat = ['None']

        #
        # PREVIEW image : get from md
        #
        if md.Meta.get('preview'):
            self.preview = md.Meta.get('preview')[0]
        # else:
        #     self.preview = const.DEFAULT_PREVIEW

        #
        # DATECR : get from md or create from OS fs metas
        #
        if md.Meta.get('datecr'):
            self.ctime = utils.to_epoch(md.Meta.get('datecr')[0])
        else:
            self.ctime = os.stat(self.f_url).st_ctime
            wmd.append(('datecr', utils.to_datestr(self.ctime)))

        self.cyear = utils.to_datestr(self.ctime,
                                      out_format='%Y')

        # WRITE missing metadatas in .md
        if len(wmd) > 0:
            self.write(wmd)



    def write(self, data_to_write: list):
        """Write metadatas to .md file
        """
        with open(self.f_url,
                  mode='r+',
                  encoding='utf-8') as md:
            mdl = md.readlines()

            # Loop into list of data to be written in md
            # d = tuples (tag, data)
            # example : ("title", "My first post !")
            for d in data_to_write:
                mdl.insert(0, f'{d[0]}:{d[1]}\n')

            mdl = ''.join(mdl)
            md.seek(0)
            md.write(mdl)



    def build_url(self) -> str:
        """Build URL from the title

        Replaces spaces by underscores, clear trash
        words and dashes, makes it short, process dupes
        and translated posts the right way."""

        # "Trash words" list
        tw = ('with','avec','under',
              'sous','the', 'for')

        url = self.title

        # Remove dashes
        url = url.replace('-', '')

        # Make list from str
        wds = url.split(' ')

        # Parse words and rm short/trash ones
        for w in list(wds):
            if (len(w) < 3) or (w in tw):
                wds.remove(w)

        # Make string from lasting words separated with
        # underscores and limit its lenght
        url = '_'.join(wds)
        url = url[:const.URL_LEN]

        # Clean '_' and 1-letter endings
        while (url[-1:] == '_') or (url[-2:-1] == '_'):
            url = url[:-1]

        # Remove accents
        url = unicodedata.normalize('NFKD', url)
        url = u"".join([c for c in url if not unicodedata.combining(c)])
        # TODO filtrer caractères spéciaux (? ! etc.)
        # avec regex, comme pour email

        # Lower case
        url = url.lower()

        # Translation post support
        if url in Md.urls \
        and self.lang \
        and self.lang != const.DEFAULT_LANG:
                url = f'{self.lang[:2]}_{url}'

        # Dupe url
        elif url in Md.urls:
            url = f"{url}_dupe_{time.time()}"

        return url



    # def build_title(self):
    #     """ Build title from file name
    #     """
        # with open(self.f_url,
        #           mode='r+',
        #           encoding='utf-8') as md:
        #     mdl = md.readlines()

        # titl = None

        # for l in mdl:
        #     if l[:2] == '# ':
        #         titl = l[2:]
        #         break
        #     elif l[:3] == '## ':
        #         titl = l[3:]
        #         break
        #     elif l[:4] == '### ':
        #         titl = l[4:]
        #         break
        #     elif l[:5] == '#### ':
        #         titl = l[5:]
        #         break

        # if titl:
        #     titl = titl.replace('\n','')
        #     return titl

        # else:
        #     return 'Untitled'
 


    # def md_checkup():
    """Vérif complète des md.

    TODO Loop sur tous les fichiers md comportant un id, pour vérifier qu'il
    existe bien un post à l'id correspondant dans le JSON
    S'il existe un id, vérifier que 1) la date de création est ==,
    2) le checksum(title + content) est ==
    """
    # for f in os.listdir(const.MD_PATH):
    #     f_url = f'{const.MD_PATH}/{f}'

    #     if f[-3:] == '.md':     
    #         md = Md(f_url)

    #         # SKIP file if a post with same title or checksum exists in JSON data
    #         if md.title in jd().titles:
    #             log.info(f'| A post with title {md.title} already exists in data.json -> skipping {f}')
    #             continue
    #         if md.sum in jd().sums:
    #             log.info(f'| A post with the same content as {f} exists in data.json -> skipping {f}')
    #             continue


    # @staticmethod
    # def process_ressources(content):
    """Lire le contenu du .md, puis vérifier la présence de lignes
    au format ![*](*.png/jpg/gif/svg)
    """
    # In content, find regex ![*](*.jpg) or one of the others formats
    # The * preceding extension only accepts alphanumeric, dash and underscore chars
    # The goal here is to detect simple filenames (without url format like https://...)
    #  which means they are local images
    # Ex : ![](hellow.svg), ![A landscape](landsc.png), etc.
        # import re
        # x = re.findall("!\[.*\]\([a-zA-ZÀ-ÿ0-9_-]*\.(?:jpg|gif|png|svg)\)", content)

        # for i in x:
        #     log.info(i, 'non traité')