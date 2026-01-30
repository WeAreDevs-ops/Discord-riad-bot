import 'dotenv/config';
import { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder, ButtonBuilder, ButtonStyle, ActionRowBuilder, InteractionType, ComponentType } from 'discord.js';
import asyncio from 'node:timers/promises';

const TOKEN = process.env.DISCORD_TOKEN;
const CLIENT_ID = process.env.CLIENT_ID; // Your bot application ID

if (!TOKEN || !CLIENT_ID) throw new Error("Missing DISCORD_TOKEN or CLIENT_ID in environment variables");

// Initialize client
const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.MessageContent] });

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
                  .setRequired(true)
        )
        .toJSON()
];

// Register global commands
const rest = new REST({ version: '10' }).setToken(TOKEN);

client.once('ready', async () => {
    console.log(`Logged in as ${client.user.tag}`);

    try {
        await rest.put(Routes.applicationCommands(CLIENT_ID), { body: commands });
        console.log('Successfully synced global commands!');
    } catch (error) {
        console.error(error);
    }
});

// Handle slash commands
client.on('interactionCreate', async (interaction) => {
    if (interaction.type !== InteractionType.ApplicationCommand) return;
    if (interaction.commandName === 'setmessage') {
        const message = interaction.options.getString('message');
        userMessages.set(interaction.user.id, message);

        // Embed message
        const embed = {
            title: 'Message Setup Complete',
            description: `Your message is set to: **${message}**\n\nClick the button below to send it 10 times in this channel.`,
            color: 0x0099ff
        };

        // Button
        const button = new ButtonBuilder()
            .setCustomId('activate')
            .setLabel('Activate')
            .setStyle(ButtonStyle.Success);

        const row = new ActionRowBuilder().addComponents(button);

        // Send reply based on context
        if (!interaction.guild) {
            // DM
            await interaction.reply({ embeds: [embed], components: [row], ephemeral: true });
        } else {
            // Server
            await interaction.reply({ embeds: [embed], components: [row], ephemeral: true });
        }
    }
});

// Handle button clicks
client.on('interactionCreate', async (interaction) => {
    if (interaction.type !== InteractionType.MessageComponent) return;
    if (interaction.customId === 'activate') {
        const userId = interaction.user.id;
        const message = userMessages.get(userId);

        if (!message) {
            await interaction.reply({ content: 'No message found. Please use /setmessage first.', ephemeral: true });
            return;
        }

        await interaction.reply({ content: 'Starting to send messages...', ephemeral: true });

        // Determine where to send
        const targetChannel = interaction.channel;

        // Spam 10 times with short delay
        for (let i = 0; i < 10; i++) {
            try {
                await targetChannel.send(message);
                await asyncio.setTimeout(300); // 0.3s delay
            } catch (err) {
                console.error('Failed to send message:', err);
            }
        }
    }
});

client.login(TOKEN);
