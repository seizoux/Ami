from PIL import Image, ImageDraw, ImageFont, ImageFilter
import typing
from io import BytesIO
import discord
import humanize
from discord.ext import commands

def welcome_func(pfp: discord.Member, member_name: str, member_disc: str, member_count: int):
    with Image.open("welcome_bg/welcome_bg.png").convert("RGBA") as wel_bg:

        with Image.open(pfp).convert("RGBA") as pfp_1:
            im = pfp_1.resize((370,370))
            bigsize = (im.size[0] * 3, im.size[1] * 3)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(im.size, Image.ANTIALIAS)
            im.putalpha(mask)
            wel_bg.paste(im,(550,50),im)
            im.close()

        with Image.open("assets/circle.png").convert("RGBA") as circle:
            im = circle.resize((418,423))
            wel_bg.paste(im,(527,25), im)
            im.close()

        font = ImageFont.truetype("fonts/antom.ttf", 92)
        font2 = ImageFont.truetype("fonts/antom.ttf", 60)
        draw = ImageDraw.Draw(wel_bg)
        h = "You are our {} member.".format(humanize.ordinal(member_count))
        s = h.upper()
        tex = f"Welcome {member_name if len(member_name) <= 10 else member_name[:10] + '...'}#{member_disc}!"
        text = tex.upper()
        x, y = 722, 560
        x2, y2 = 742, 700
        fillcolor = "white"
        shadowcolor = "black"
        shadowcolor2 = "black"

        # thin border
        draw.text((x-1, y), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x+1, y), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x, y-1), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x, y+1), text, font=font, fill=shadowcolor, anchor="ms")

        # thicker border
        draw.text((x-1, y-1), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x+1, y-1), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x-1, y+1), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x+1, y+1), text, font=font, fill=shadowcolor, anchor="ms")

        draw.text((x, y), text, font=font, fill=fillcolor, anchor="ms")

        # thin border
        draw.text((x2-1, y2), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2+1, y2), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2, y2-1), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2, y2+1), s, font=font2, fill=shadowcolor2, anchor="ms")

        # thicker border
        draw.text((x2-1, y2-1), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2+1, y2-1), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2-1, y2+1), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2+1, y2+1), s, font=font2, fill=shadowcolor2, anchor="ms")

        draw.text((x2, y2), s, font=font2, fill=fillcolor, anchor="ms")

        buffer = BytesIO()
        wel_bg.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

def round_func(pfp: discord.Member):
    with Image.open(pfp).convert("RGBA") as pfp_1:
        im = pfp_1.resize((370,370))
        bgs = Image.new("RGBA", (0,0), 0)
        bg = bgs.resize(im.size, Image.ANTIALIAS)
        bigsize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        im.putalpha(mask)
        bg.paste(im,(0,0),im)
        im.close()

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

class RankCard:
  """
  A class function to draw our rank card
  """

  def drawProgressBar(d, x, y, w, h, progress, fg="#DC143C"):

      w *= progress
      d.ellipse((x+w, y, x+h+w, y+h),fill=fg)
      d.ellipse((x, y, x+h, y+h),fill=fg)
      d.rectangle((x+(h/2), y, x+w+(h/2), y+h),fill=fg)

      return d

  def levelup_func(avatar: discord.Member, level:str):
      with Image.open("assets/levelup.png").convert("RGBA") as bg:
          bg = bg.resize((230, 100))

          with Image.open("assets/glass.png").convert("RGBA") as glass:
              im = glass.resize((150, 90))
              bg.paste(im, (70, 5), im)
              im.close()

          with Image.open(avatar).convert("RGBA") as pfp_1:
              im = pfp_1.resize((85, 85))
              bg.paste(im,(9, 8),im)
              im.close()

          font = ImageFont.truetype("fonts/antom.ttf", 28)
          draw = ImageDraw.Draw(bg)
          text = f"{level}"
          text2 = "LEVEL UP!"
          color = "white"
          color2 = "gold"
          shadow = "black"

          x, y = 150, 70
          x2, y2 = 105, 10

          draw.text((x-1, y), text, font=font, fill=shadow, anchor="mm")
          draw.text((x+1, y), text, font=font, fill=shadow, anchor="mm")
          draw.text((x, y-1), text, font=font, fill=shadow, anchor="mm")
          draw.text((x, y+1), text, font=font, fill=shadow, anchor="mm")

          # thicker border
          draw.text((x-1, y-1), text, font=font, fill=shadow, anchor="mm")
          draw.text((x+1, y-1), text, font=font, fill=shadow, anchor="mm")
          draw.text((x-1, y+1), text, font=font, fill=shadow, anchor="mm")
          draw.text((x+1, y+1), text, font=font, fill=shadow, anchor="mm")

          draw.text((x, y), text, font=font, fill=color, anchor="mm")

          draw.text((x2-1, y2), text2, font=font, fill=shadow)
          draw.text((x2+1, y2), text2, font=font, fill=shadow)
          draw.text((x2, y2-1), text2, font=font, fill=shadow)
          draw.text((x2, y2+1), text2, font=font, fill=shadow)

          # thicker border
          draw.text((x2-1, y2-1), text2, font=font, fill=shadow)
          draw.text((x2+1, y2-1), text2, font=font, fill=shadow)
          draw.text((x2-1, y2+1), text2, font=font, fill=shadow)
          draw.text((x2+1, y2+1), text2, font=font, fill=shadow)

          draw.text((x2, y2), text2, font=font, fill=color2)

          buffer = BytesIO()
          bg.save(buffer, format="PNG")
          buffer.seek(0)

          return buffer

  def level_func(avatar: discord.Member, name:str, disc:str, level:int, xp:int, needed:int, rank:str):
      with Image.open("assets/level_card.png").convert("RGBA") as bg:

          with Image.open(avatar).convert("RGBA") as pfp_1:
              im = pfp_1.resize((241, 242))
              bigsize = (im.size[0] * 3, im.size[1] * 3)
              mask = Image.new('L', bigsize, 0)
              draw = ImageDraw.Draw(mask) 
              draw.ellipse((0, 0) + bigsize, fill=255)
              mask = mask.resize(im.size, Image.ANTIALIAS)
              im.putalpha(mask)
              bg.paste(im,(34,19),im)
              im.close()
        
          exp = int(xp)
          need = int(needed)
          spkx, spky = 355, 216

          sparky = 0.00
          x_sparky = int(need/100)
          f = x_sparky
          for i in range(100):
              if exp >= x_sparky:
                  sparky += 0.01
                  x_sparky += f

          d = ImageDraw.Draw(bg)
          d = RankCard.drawProgressBar(d, spkx, spky+10, 815, 30, sparky)

          font = ImageFont.truetype("fonts/ArialUnicodeMS.ttf", 58)
          font_disc = ImageFont.truetype("fonts/ArialUnicodeMS.ttf", 35)
          font2 = ImageFont.truetype("fonts/louis.ttf", 38)
          font3 = ImageFont.truetype("fonts/louis.ttf", 42)
          font4 = ImageFont.truetype("fonts/louis.ttf", 70)
          font5 = ImageFont.truetype("fonts/louis.ttf", 36)
          font6 = ImageFont.truetype("fonts/louis.ttf", 45)
          font7 = ImageFont.truetype("fonts/louis.ttf", 78)
          draw = ImageDraw.Draw(bg)

          # colors
          color = "#F8F8FF"
          color2 = "white"

          #TEXTS
          member_name = name
          member_disc = disc
          level_text = f"LVL."
          level_number_text = f"{level}"
          xp_text = f"{xp:,} XP /"
          needed_xp_text = f"{need:,}"
          rank_text = "RANK"
          rank_number_text = f"#{rank}"

          #coords
          x, y = 355, 28
          x2, y2 = 360, 130
          x3, y3 = 365 + font.getsize(member_name)[0], 53
          x4 = 370 + font3.getsize(xp_text)[0]
          x5 = 1010 + font4.getsize(level_text)[0]
          x6, y6 = 955, 50
          x7 = 965 + font6.getsize(rank_text)[0]

          # drawing member rank text
          draw.text((x6, y6), rank_text, font=font6, fill="white")

          # drawing member rank number
          draw.text((x7, y6-30), rank_number_text, font=font7, fill="#DC143C")

          # drawing member name
          if len(member_name) >= 10:
              font = ImageFont.truetype("fonts/ArialUnicodeMS.ttf", 38)
              y += 12
              x3, y3 = 360 + font.getsize(member_name)[0], 42
          draw.text((x-1, y+1), member_name, font=font, fill="black")
          draw.text((x-2, y+2), member_name, font=font, fill="black")
          draw.text((x, y), member_name, font=font, fill=color)

          # drawing member disc
          draw.text((x3, y3), member_disc, font=font_disc, fill="#DC143C")

          # drawing member level text
          draw.text((x2+700, y2+40), level_text, font=font2, fill=color2)

          # drawing member level number with border bold black
          draw.text((x5, y2+10), level_number_text, font=font4, fill="#DC143C")

          # drawing member xp
          draw.text((x2, y2+40), xp_text, font=font3, fill="#DC143C")
          draw.text((x2-1, (y2+40)-1), xp_text, font=font3, fill="#DC143C")

          # drawing member needed xp with border bold black
          draw.text((x4, y2+44), needed_xp_text, font=font5, fill="#DCDCDC")

          buffer = BytesIO()
          bg.save(buffer, format="PNG")
          buffer.seek(0)

          return buffer

class GayMeter:
    def gaymeter_func(pfp: discord.Member, perc:int):
        with Image.open("assets/gaymeter.png") as bg:

            x, y = 134, 576

            for i in range(perc):
                y -= 6

            with Image.open(pfp).convert("RGBA") as pfp_1:
                im = pfp_1.resize((100, 100))
                bigsize = (im.size[0] * 3, im.size[1] * 3)
                mask = Image.new('L', bigsize, 0)
                draw = ImageDraw.Draw(mask) 
                draw.ellipse((0, 0) + bigsize, fill=255)
                mask = mask.resize(im.size, Image.ANTIALIAS)
                im.putalpha(mask)
                bg.paste(im,(x, y),im)
                im.close()

            buffer = BytesIO()
            bg.save(buffer, format="PNG")
            buffer.seek(0)

            return buffer

class Ship:
    def ShipBar(d, x, y, w, h, progress, fg="#DC143C"):

        w *= progress
        d.ellipse((x+w, y, x+h+w, y+h),fill=fg)
        d.ellipse((x, y, x+h, y+h),fill=fg)
        d.rectangle((x+(h/2), y, x+w+(h/2), y+h),fill=fg)

        return d


    def ship_func(perc:int, pfp: discord.Member, pfp2: discord.Member = None):
        with Image.open("assets/ship_banner.png") as bg:

            with Image.open(pfp).convert("RGBA") as pfp_1:
              im = pfp_1.resize((256, 258))
              bigsize = (im.size[0] * 3, im.size[1] * 3)
              mask = Image.new('L', bigsize, 0)
              draw = ImageDraw.Draw(mask) 
              draw.ellipse((0, 0) + bigsize, fill=255)
              mask = mask.resize(im.size, Image.ANTIALIAS)
              im.putalpha(mask)
              bg.paste(im,(65,25),im)
              im.close()


            with Image.open(pfp2).convert("RGBA") as pfp_2:
              im = pfp_2.resize((260, 258))
              bigsize = (im.size[0] * 3, im.size[1] * 3)
              mask = Image.new('L', bigsize, 0)
              draw = ImageDraw.Draw(mask) 
              draw.ellipse((0, 0) + bigsize, fill=255)
              mask = mask.resize(im.size, Image.ANTIALIAS)
              im.putalpha(mask)
              bg.paste(im,(972,22),im)
              im.close()

            sparky = 0.00
            x_sparky = int(perc/100)
            d = 0
            f = x_sparky
            for i in range(100):
                d += 1
                sparky += 0.01
                x_sparky += f
                if d >= perc:
                    break

            d = ImageDraw.Draw(bg)
            d = Ship.ShipBar(d, 380, 212, 500, 40, sparky)

            font = ImageFont.truetype("fonts/love.ttf", 180)
            draw = ImageDraw.Draw(bg)
            text = f"{perc}%"
            x, y = 640, 150
            fillcolor = "pink"
            shadowcolor = "black"

            # thin border
            draw.text((x-1, y), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x+1, y), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x, y-1), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x, y+1), text, font=font, fill=shadowcolor, anchor="mm")

            # thicker border
            draw.text((x-1, y-1), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x+1, y-1), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x-1, y+1), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x+1, y+1), text, font=font, fill=shadowcolor, anchor="mm")

            draw.text((x, y), text, font=font, fill=fillcolor, anchor="mm")

            buffer = BytesIO()
            bg.save(buffer, format="PNG")
            buffer.seek(0)

            return buffer

def lead_func(pfp: typing.List[BytesIO], user_name:str, user_bal:str):
    with Image.open("assets/leaderboard.png") as bg:

        font = ImageFont.truetype("fonts/bebas.ttf", 90)
        font2 = ImageFont.truetype("fonts/antom.ttf", 125)
        draw = ImageDraw.Draw(bg)

        text = f"{user_name}"

        text2 = f"{user_bal}"

        x, y = 130, 200

        x2, y2 = x+1300, y

        fillcolor = "#6495ED"
        shadowcolor = "black"

        fillcolor2 = "#DC143C"
        shadowcolor2 = "black"

        # thin border
        draw.text((x-1, y), text, font=font, fill=shadowcolor)
        draw.text((x+1, y), text, font=font, fill=shadowcolor)
        draw.text((x, y-1), text, font=font, fill=shadowcolor)
        draw.text((x, y+1), text, font=font, fill=shadowcolor)

        # thicker border
        draw.text((x-1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x-1, y+1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y+1), text, font=font, fill=shadowcolor)

        draw.text((x, y), text, font=font, fill=fillcolor)

        # thin border
        draw.text((x2-1, y2), text2, font=font, fill=shadowcolor2)
        draw.text((x2+1, y2), text2, font=font, fill=shadowcolor2)
        draw.text((x2, y2-1), text2, font=font, fill=shadowcolor2)
        draw.text((x2, y2+1), text2, font=font, fill=shadowcolor2)

        # thicker border
        draw.text((x2-1, y2-1), text2, font=font, fill=shadowcolor2)
        draw.text((x2+1, y2-1), text2, font=font, fill=shadowcolor2)
        draw.text((x2-1, y2+1), text2, font=font, fill=shadowcolor2)
        draw.text((x2+1, y2+1), text2, font=font, fill=shadowcolor2)

        draw.text((x2, y2), text2, font=font, fill=fillcolor2)

        x3, y3 = x-90, y
        for i in pfp:
            y3 += 86
            with Image.open(i).convert("RGBA") as pfp:
                image1 = pfp.resize((80,80), resample=Image.NEAREST, reducing_gap=1)
                bg.paste(image1,(x3,y3-80))
                image1.close()

        buffer = BytesIO()
        bg.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

def setup(bot):
    print("[SETUP] Definitions")

def teardown(bot):
    print("[TEARDOWN] Definitions")