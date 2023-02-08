using System;
using System.Reflection;

using FezGame;
using FezGame.Components;
using FezGame.Services;
using FezEngine.Structure;
using FezEngine.Tools;

using Microsoft.Xna.Framework;

using MonoMod.RuntimeDetour;

namespace Randomizer
{
	public class ClockTowerHelper : GameComponent
	{

        private static Type ClockTowerHostType;

		private static IDetour ClockDetour;

		public static Fez Fez;

        public ClockTowerHelper(Game game): base(game)
		{
			Fez = (Fez)game;
			ClockTowerHostType = Assembly.GetAssembly(typeof(Fez)).GetType("FezGame.Components.ClockTowerHost");

			ClockDetour = new Hook(
				ClockTowerHostType.GetMethod("TestSecretFor", BindingFlags.NonPublic | BindingFlags.Instance),
				new Func<Func<object, bool, ArtObjectInstance, TrileInstance, TrileInstance, TrileInstance>, object, bool, ArtObjectInstance, TrileInstance, TrileInstance, TrileInstance>((orig, self, condition, ao, secret, topMost) =>
				{
					return orig(self, true, ao, secret, topMost);
				}
			));
        }
	}
}

