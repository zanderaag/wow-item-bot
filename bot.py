import io, csv, os, discord, string, time
from time import sleep
from discord import Embed
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

client = commands.Bot(command_prefix = '.')

with open('token.txt', 'r') as t:
	token = t.readline()

#default windows paths to the extensions when you package the extensions in about://extensions. change version numbers as needed.
extension_one = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Extensions\odhmfmnoejhihkmfebnolljiibpnednn\1.7.0_0.crx')
extension_two = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Extensions\cjpalhdlnbpafiamejdnhcphjbkeiagm\1.29.2_0.crx')

def formatName(entryId,itemName):
	item_id = entryId
	item_name = itemName.lower()
	formatted_name = item_name.replace(",","")
	new_name = formatted_name.split()
	newer_name = '-'.join(new_name)
	return newer_name, item_id
	
def return_args(args):
	global fullName
	global fullNames
	global capitalized_names
	fullNames = []
	capitalized_names = []
	l_string = ' '.join(args)
	new_string = l_string.split()
	newer_string = '-'.join(new_string)
	with open('items.csv', 'r') as csv_file:
		reader = csv.reader(csv_file)

		for entry,name in reader:    
			if l_string.lower() == name.lower():
				print(formatName(entry,name))
				fullName = name
				return formatName(entry,name)    

		csv_file.seek(0)

		for entry,name in reader:
			if l_string.lower() in name.lower():
				print(formatName(entry,name))
				fullName = name
				fullNames += formatName(entry,name)
				capitalized_names.append(name)
		return fullNames

def make_photo_directory():
	if not os.path.isdir('./tooltips'):
		os.mkdir('tooltips')
	if not os.path.isdir('./thumbnails'):
		os.mkdir('thumbnails')



@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

@client.command()
async def item(ctx, *args):
	global message_id_global
	newer_name = return_args(args)
	print(newer_name)
	print(capitalized_names)
	#if only one match is found, grab the exact match and display it to the user
	if len(newer_name) == 2:
		try:
			if os.path.isfile('./tooltips/' + f'{newer_name[0]}.png'):
				print("This text appears if the tooltip requested is already cached. Skipping GET request...")
				
				with open('./tooltips/' + f'{newer_name[0]}.png', 'rb') as f:
					embed = discord.Embed(title=f'{fullName}', color=0xFFA500) #creates embed
					item_file = discord.File('./tooltips/' + f'{newer_name[0]}.png', filename="image.png")
					tt_file = discord.File('./thumbnails/' + f'{newer_name[0]}.png', filename="image2.png")
					embed.set_image(url="attachment://image.png")
					embed.set_thumbnail(url="attachment://image2.png")
					await ctx.send(files=[item_file, tt_file], embed=embed)
			else:
				chrome_options = Options()
				chrome_options.add_extension(extension_one)
				chrome_options.add_extension(extension_two)
				chromer = webdriver.Chrome(options=chrome_options)
				chromer.get(f'https://classic.wowhead.com/item={newer_name[1]}/{newer_name[0]}')
				image = chromer.find_element_by_id(f'tt{newer_name[1]}')
				sleep(1)
				image.screenshot('./tooltips/' + f'{newer_name[0]}.png')
				image2 = chromer.find_element_by_id(f'ic{newer_name[1]}')
				sleep(1)
				image2.screenshot('./thumbnails/' + f'{newer_name[0]}.png')
				chromer.quit()

				with open('./tooltips/' + f'{newer_name[0]}.png', 'rb') as f:
					embed = discord.Embed(title=f'{fullName}', color=0xFFA500) #creates embed
					item_file = discord.File('./tooltips/' + f'{newer_name[0]}.png', filename="image.png")
					tt_file = discord.File('./thumbnails/' + f'{newer_name[0]}.png', filename="image2.png")
					embed.set_image(url="attachment://image.png")
					embed.set_thumbnail(url="attachment://image2.png")
					await ctx.send(files=[item_file, tt_file], embed=embed)
		except Exception as e:
			await ctx.send("An error occured internally. Please try refining your search query or contact the dev. Coffee required.")
			print(e)
	#if more than one match is found, display x amount of results that contain the search term to the user so they can copypaste in what they want
	elif len(newer_name) > 2:
		new_list = newer_name[0:9:2]
		id_list = newer_name[1:10:2]
		print(id_list)
		newish_list = []
		counter = 0
		for name in new_list:
			newname = name.split("-")
			newname2 = " ".join(newname)
			newname3 = string.capwords(newname2)
			newish_list.append(str(counter + 1) + '. ' + newname3)
			counter += 1
			#newname to be used to query based on the emoji reaction given(1-5)
			print(newname3)
		newish_list.insert(0, "**Did you mean one of the following?**")
		newish_list = '\n'.join(newish_list)
		new_msg = await ctx.send(newish_list)
		emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
		new_count = 0
		while counter != 0:
			await new_msg.add_reaction(emoji[new_count])
			counter -= 1
			new_count += 1

		def check(reaction, user):
			return user == ctx.message.author and str(reaction.emoji) in emoji
	try:
		reaction, user = await client.wait_for('reaction_add', timeout=30, check=check)
		choice = emoji.index(reaction.emoji)
		print(choice)
		selected_reaction_item = [new_list[choice],id_list[choice]]
		selected_reaction_item_fullname = capitalized_names[choice]
		print(selected_reaction_item)
		print(selected_reaction_item_fullname)
		if os.path.isfile('./tooltips/' + f'{selected_reaction_item[0]}.png'):
			print("This text appears if the tooltip requested is already cached. Skipping GET request...")
			with open('./tooltips/' + f'{selected_reaction_item[0]}.png', 'rb') as f:
				embed = discord.Embed(title=f'{capitalized_names[choice]}', color=0xFFA500) #creates embed
				item_file = discord.File('./tooltips/' + f'{selected_reaction_item[0]}.png', filename="image.png")
				tt_file = discord.File('./thumbnails/' + f'{selected_reaction_item[0]}.png', filename="image2.png")
				embed.set_image(url="attachment://image.png")
				embed.set_thumbnail(url="attachment://image2.png")
				await ctx.send(files=[item_file, tt_file], embed=embed)
		else:
			chrome_options = Options()
			chrome_options.add_extension(extension_one)
			chrome_options.add_extension(extension_two)
			chromer = webdriver.Chrome(options=chrome_options)
			chromer.get(f'https://classic.wowhead.com/item={selected_reaction_item[1]}/{selected_reaction_item[0]}')
			image = chromer.find_element_by_id(f'tt{selected_reaction_item[1]}')
			sleep(1)
			image.screenshot('./tooltips/' + f'{selected_reaction_item[0]}.png')
			image2 = chromer.find_element_by_id(f'ic{selected_reaction_item[1]}')
			sleep(1)
			image2.screenshot('./thumbnails/' + f'{selected_reaction_item[0]}.png')
			chromer.quit()

			with open('./tooltips/' + f'{selected_reaction_item[0]}.png', 'rb') as f:
				embed = discord.Embed(title=f'{capitalized_names[choice]}', color=0xFFA500) #creates embed
				item_file = discord.File('./tooltips/' + f'{selected_reaction_item[0]}.png', filename="image.png")
				tt_file = discord.File('./thumbnails/' + f'{selected_reaction_item[0]}.png', filename="image2.png")
				embed.set_image(url="attachment://image.png")
				embed.set_thumbnail(url="attachment://image2.png")
				await ctx.send(files=[item_file, tt_file], embed=embed)
		
	except Exception as e:
		print(e)
	
client.run(token)
