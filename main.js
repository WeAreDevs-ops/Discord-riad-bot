// main.js
import 'dotenv/config';
import { Client, GatewayIntentBits, Partials, ActionRowBuilder, ButtonBuilder, ButtonStyle, Events, REST, Routes, SlashCommandBuilder } from 'discord.js';

const TOKEN = process.env.DISCORD_TOKEN;
if (!TOKEN) throw new Error("DISCORD_TOKEN not found in environment variables");

// Create bot client
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.DirectMessages,
        GatewayIntentBits.MessageContent
    ],
    partials: [Partials.Channel] // Needed for DMs
});

// In-memory storage for user messages
const userMessages = new Map();

// Define slash command
const commands = [
    new SlashCommandBuilder()
        .setName('setmessage')
        .setDescription('Setup the message to be spammed')
        .addStringOption(option =>
            option.setName('message')
                .setDescription('The message you want to spam')
                .setRequired(true))
        .toJSON()
];

// Register global slash commands
const rest = new REST({ version: '10' }).setToken(TOKEN);
(async () => {
    try {
        console.log('Started refreshing application (/) commands.');
        await rest.put(Routes.applicationCommands(client.user?.id ?? '1425782268403646518'), { body: commands });
        console.log('Successfully reloaded application (/) commands.');
    } catch (error) {
        console.error(error);
    }
})();

// Handle slash commands
client.on(Events.InteractionCreate, async interaction => {
    if (!interaction.isChatInputCommand() && !interaction.isButton()) return;

    if (interaction.isChatInputCommand()) {
        if (interaction.commandName === 'setmessage') {
            const message = interaction.options.getString('message');
            userMessages.set(interaction.user.id, message);

            // Create a button
            const row = new ActionRowBuilder()
                .addComponents(
                    new ButtonBuilder()
                        .setCustomId('activate')
                        .setLabel('Activate')
                        .setStyle(ButtonStyle.Success)
                );

            await interaction.reply({
                content: `Your message is set to: **${message}**\nClick the button below to send it 10 times.`,
                components: [row],
                ephemeral: true
            });
        }
    }

    if (interaction.isButton()) {
        if (interaction.customId === 'activate') {
            const message = userMessages.get(interaction.user.id);
            if (!message) {
                await interaction.reply({ content: 'You have not set a message yet.', ephemeral: true });
                return;
            }

            await interaction.reply({ content: 'Starting to send messages...', ephemeral: true });

            // Send 10 messages with slight delay
            for (let i = 0; i < 10; i++) {
                try {
                    await interaction.channel.send(message);
                    await new Promise(res => setTimeout(res, 300)); // 0.3s delay
                } catch (err) {
                    console.error(err);
                }
            }
        }
    }
});

// Log in
client.once(Events.ClientReady, c => {
    console.log(`Logged in as ${c.user.tag}`);
});

client.login(TOKEN);
