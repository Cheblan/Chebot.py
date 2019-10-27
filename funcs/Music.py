class Music:
    def __init__(self, bot):
        self.bot = bot
        self.music_states = {}

    def __unload(self):
        for state in self.music_states.values():
            self.bot.loop.create_task(state.stop())

    def __local_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command cannot be used in a private message.')
        return True

    async def __before_invoke(self, ctx):
        ctx.music_state = self.get_music_state(ctx.guild.id)

    async def __error(self, ctx, error):
        if not isinstance(error, commands.UserInputError):
            raise error

        try:
            await ctx.send(error)
        except discord.Forbidden:
            pass  # /shrug

    def get_music_state(self, guild_id):
        return self.music_states.setdefault(guild_id, GuildMusicState(self.bot.loop))

    @commands.command()
    async def status(self, ctx):
        if ctx.music_state.is_playing():
            song = ctx.music_state.current_song
            await ctx.send(f'Играет {song} на громкости {song.volume * 100}% в {ctx.voice_client.channel.mention}')
        else:
            await ctx.send('Ничего не играет.')

    @commands.command()
    async def playlist(self, ctx):
        await ctx.send(f'{ctx.music_state.playlist}')

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        if channel is None and not ctx.author.voice:
            raise MusicError('Зайдите в голосовой канал, чтобы пригласить бота.')

        destination = channel or ctx.author.voice.channel

        if ctx.voice_client:
            await ctx.voice_client.move_to(destination)
        else:
            ctx.music_state.voice_client = await destination.connect()

    @commands.command()
    async def play(self, ctx, *, request: str):
        await ctx.message.add_reaction('\N{HOURGLASS}')

        # Create the SongInfo
        song = await SongInfo.create(request, ctx.author, ctx.channel, loop=ctx.bot.loop)

        # Connect to the voice channel if needed
        if ctx.voice_client is None or not ctx.voice_client.is_connected():
            await ctx.invoke(self.join)

        # Add the info to the playlist
        try:
            ctx.music_state.playlist.add_song(song)
        except asyncio.QueueFull:
            raise MusicError('Плейлист полный, попробуйте позже.')

        if not ctx.music_state.is_playing():
            # Download the song and play it
            await song.download(ctx.bot.loop)
            await ctx.music_state.play_next_song()
        else:
            # Schedule the song's download
            ctx.bot.loop.create_task(song.download(ctx.bot.loop))
            await ctx.send(f'Песня {song} добавлена на позиции **#{ctx.music_state.playlist.qsize()}**')

        await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @play.error
    async def play_error(self, ctx, error):
        await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
        await ctx.message.add_reaction('\N{CROSS MARK}')

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def pause(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.pause()

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def resume(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.resume()

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def stop(self, ctx):
        await ctx.music_state.stop()

    @commands.command()
    async def volume(self, ctx, volume: int = None):
        if volume < 0 or volume > 100:
            raise MusicError('Громкость должна быть от 0 до 100.')
        ctx.music_state.volume = volume / 100

    @commands.command()
    async def clear(self, ctx):
        ctx.music_state.playlist.clear()

    @commands.command()
    async def skip(self, ctx):
        if not ctx.music_state.is_playing():
            raise MusicError('Пропускать нечего.')

        if ctx.author.id in ctx.music_state.skips:
            raise MusicError(f'{ctx.author.mention}, вы уже голосовали за пропуск.')

        # Count the vote
        ctx.music_state.skips.add(ctx.author.id)
        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

        # Check if the song has to be skipped
        if len(
                ctx.music_state.skips) > ctx.music_state.min_skips or ctx.author == ctx.music_state.current_song.requester:
            ctx.music_state.skips.clear()
            ctx.voice_client.stop()

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def minskips(self, ctx, number: int):
        ctx.music_state.min_skips = number
