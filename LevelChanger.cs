using System;
using System.Reflection;
using Microsoft.Xna.Framework;

using FezGame;
using FezGame.Components;
using FezGame.Structure;
using FezGame.Services;
using FezEngine.Effects;
using FezEngine.Effects.Structures;
using FezEngine.Tools;

using MonoMod.RuntimeDetour;

namespace Randomizer
{
    public class LevelChanger : GameComponent
    {
        private static IDetour LevelChangeHook;

        private static Type LevelManagerType;

        [ServiceDependency]
        public IGameLevelManager LevelManager { private get; set; }

        [ServiceDependency]
        public IPlayerManager PlayerManager { private get; set; }

        [ServiceDependency]
        public IGameCameraManager CameraManager { private get; set; }

        public static Fez Fez { get; private set; }

        public LevelChanger(Game game) : base(game)
        {
            Fez = (Fez)game;

            LevelManagerType = Assembly.GetAssembly(typeof(Fez)).GetType("FezGame.Services.GameLevelManager");

            LevelChangeHook = new Hook(
                LevelManagerType.GetMethod("ChangeLevel"),
                new Action<Action<object, string>, object, string>((orig, self, level_name) => {
                    if (level_name == "GOMEZ_HOUSE")
                    {
                        var manager = (GameLevelManager)self;
                        manager.DestinationVolumeId = 3;
                        orig(self, "WATERFALL");
                        CameraManager.AlterTransition(FezEngine.Viewpoint.Back);
                    }
                    else
                    {
                        orig(self, level_name);
                    }
                }
            ));
        }

        protected override void Dispose(bool disposing)
        {
            LevelChangeHook.Dispose();
        }
    }
}
