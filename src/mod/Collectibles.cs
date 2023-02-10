using System;
using Microsoft.Xna.Framework;
using FezGame;
using FezGame.Services;
using FezEngine.Services;
using FezEngine.Structure;
using FezEngine.Tools;
namespace Randomizer
{
	public class Collectibles
	{
		public Collectibles()
		{
            
        }

		public void PrintArtObjects(IGameLevelManager levelManager)
		{
			if(levelManager == null)
			{
				Console.WriteLine("No level manager.");
				return;
			}
			var pickups = levelManager.PickupGroups;
			foreach(var group in pickups.Values)
			{
				if(group.ActorType == ActorType.CubeShard)
				{
					Console.WriteLine("Found bit.");
                }
			}
		}
	}
}

