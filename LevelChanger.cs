using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Reflection;
using Microsoft.Xna.Framework;

using FezGame;
using FezGame.Components;
using FezGame.Components.Actions;
using FezGame.Structure;
using FezGame.Services;
using FezEngine.Effects;
using FezEngine.Effects.Structures;
using FezEngine.Tools;

using MonoMod.RuntimeDetour;
using static Randomizer.LevelChanger;

namespace Randomizer
{
    public class LevelChanger : GameComponent
    {
        public static readonly string ConfigFile = "Mods/Randomizer/config.txt";

        [Serializable]
        public struct Entrance
        {
            public string LevelFrom; // The level this entrance is connecting from.
            public string LevelToOrig; // The level this entrance would usually go to.
            public string LevelToNew; // The level this entrance goes to after randomization.
            public int DestVolumeId; // The destination volume ID of the new level.
            public string DestViewpoint; // The viewpoint to use when spawning into the new level.
        }

        private static IDetour LevelChangeHook;
        private static IDetour FarAwayHook;

        private static Type LevelManagerType;
        private static Type EnterDoorType;

        private List<Entrance> Entrances = new List<Entrance>();

        [ServiceDependency]
        public IGameLevelManager LevelManager { private get; set; }

        [ServiceDependency]
        public IGameStateManager StateManager { private get; set; }

        [ServiceDependency]
        public IPlayerManager PlayerManager { private get; set; }

        [ServiceDependency]
        public IGameCameraManager CameraManager { private get; set; }

        public static Fez Fez { get; private set; }

        public LevelChanger(Game game) : base(game)
        {
            Fez = (Fez)game;

            ParseInputFile();

            LevelManagerType = Assembly.GetAssembly(typeof(Fez)).GetType("FezGame.Services.GameLevelManager");
            EnterDoorType = Assembly.GetAssembly(typeof(Fez)).GetType("FezGame.Components.Actions.EnterDoor");

            LevelChangeHook = new Hook(
                LevelManagerType.GetMethod("ChangeLevel"),
                new Action<Action<object, string>, object, string>((orig, self, level_name) => ChangeLevelOverride(orig, self, level_name)
            ));

            FarAwayHook = new Hook(
                EnterDoorType.GetMethod("Begin", BindingFlags.NonPublic | BindingFlags.Instance),
                new Action<Action<object>, object>((orig, self) =>
                {
                    if (LevelManager.Name.StartsWith("CABIN_INTERIOR"))
                    {
                        //TODO this still looks weird, gomez is facing to the side when walking through.
                        PlayerManager.SpinThroughDoor = false;
                    }
                    LevelManager.DestinationIsFarAway = false;
                    StateManager.FarawaySettings.Reset();
                    orig(self);
                }
            ));
        }

        public void ParseInputFile()
        {
            var reader = File.OpenText(ConfigFile);

            while(!reader.EndOfStream)
            {
                Entrance entrance;
                entrance.LevelFrom = reader.ReadLine();
                entrance.LevelToOrig = reader.ReadLine();
                entrance.LevelToNew = reader.ReadLine();
                entrance.DestVolumeId = int.Parse(reader.ReadLine());
                entrance.DestViewpoint = reader.ReadLine();
                Entrances.Add(entrance);
                reader.ReadLine();
            }
        }

        public static FezEngine.Viewpoint StringToView(string view)
        {
            switch(view.ToUpper())
            {
                case "BACK":
                    return FezEngine.Viewpoint.Back;
                case "FRONT":
                    return FezEngine.Viewpoint.Front;
                case "LEFT":
                    return FezEngine.Viewpoint.Left;
                case "RIGHT":
                    return FezEngine.Viewpoint.Right;
                default:
                    return FezEngine.Viewpoint.Front;
            }
        }

        public void ChangeLevelOverride(Action<object, string> orig, object self, string level_name)
        {
            var manager = (GameLevelManager)self;
            string prevLevel = manager.Name;
            List<Entrance> matchingEntrances = Entrances.Where(entrance => entrance.LevelFrom == prevLevel && entrance.LevelToOrig == level_name).ToList();
            Console.WriteLine($"From: {prevLevel}, To: {level_name}");
            if (matchingEntrances.Count > 0)
            {
                Entrance entrance = matchingEntrances[0];

                manager.DestinationVolumeId = entrance.DestVolumeId;
                orig(self, entrance.LevelToNew);

                // For some reason, these levels crash when setting the camera.
                if(!(entrance.LevelToNew.StartsWith("CABIN_INTERIOR")))
                {
                    CameraManager.AlterTransition(StringToView(entrance.DestViewpoint));
                }
            }
            else
            {
                orig(self, level_name);
            }
        }

        protected override void Dispose(bool disposing)
        {
            LevelChangeHook.Dispose();
        }
    }
}
