#!/usr/bin/env

import rospy
from std_msgs.msg import String

recordA = {'Fire': 300, 'Water': 400, 'Earth': 500}
recordB = {'Rock': 300, 'Thunder': 400, 'Wind': 500}
msg = String()


class Player:
    def attack(self, attack_monster, opposition, type_attack, target_monster=None):
        opprecord = recordB if attack_monster in recordA else recordA
        if type_attack == 1:
            for monster in opprecord.keys():
                attacker_value = getattr(self, attack_monster)
                if attacker_value == 0:
                    msg.data = "Oops! Can't attack with a dead monster"
                    rospy.publish(msg)
                opprecord[monster] = 0 if ((opprecord[monster] - 0.1 * attacker_value) < 0) else (
                            opprecord[monster] - 0.1 * attacker_value)

        elif type_attack == 2:
            if getattr(opposition, target_monster) == 0:
                msg.data = "Oops! This monster is already dead. Cannot attack a dead monster."
                rospy.publish(msg)
                return
            if not bool(target_monster):
                msg.data = "You forgot to enter the target monster's name!"
                rospy.publish(msg)
                msg.data = f"{attack_monster}'s turn: "
                rospy.publish(msg)
            else:
                attacker_value = getattr(self, attack_monster)
                if attacker_value == 0:
                    msg.data = "Oops! Can't attack with a dead monster"
                    rospy.publish(msg)
                opprecord[target_monster] = 0 if ((opprecord[target_monster] - 0.2 * attacker_value) < 0) else (
                        opprecord[target_monster] - 0.2 * attacker_value)


class PlayerA(Player):
    def __init__(self):
        self.Fire = 300
        self.Water = 400
        self.Earth = 500


class PlayerB(Player):
    def __init__(self):
        self.Rock = 300
        self.Thunder = 400
        self.Wind = 500


def callbackA(data):
    try:
        global curr_mons
        inp = data.data.split()
        if inp[0] == '2':
            print(f"{curr_mons} attacked {inp[1]}")
            playerA.attack(curr_mons, playerB, 2, inp[1])
        else:
            print(f"{curr_mons} attacked all")
            playerA.attack(curr_mons, playerB, 1)
    except IndexError:
        playerA.attack(curr_mons, playerB, 1)


def callbackB(data):
    global curr_mons
    inp = data.data.split()
    if inp[0] == '2':
        print(f"{curr_mons} attacked {inp[1]}")
        playerB.attack(curr_mons, playerA, 2, inp[1])
    else:
        print(f"{curr_mons} attacked all")
        playerB.attack(curr_mons, playerA, 1)


playerA = PlayerA()
playerB = PlayerB()
curr_mons = ''
serverA = rospy.Publisher('write_to_A', String, queue_size=100)
receiverA = rospy.Subscriber('read_from_A', String, callbackA, queue_size=100)
serverB = rospy.Publisher('write_to_B', String, queue_size=100)
receiverB = rospy.Subscriber('read_from_B', String, callbackB, queue_size=100)


def body(pl, i):
    global serverA, serverB, receiverB, receiverA
    topic = 'read_from_A' if pl == playerA else 'read_from_B'
    opptopic = 'read_from_B' if pl == playerA else 'read_from_A'

    server = serverA if pl == playerA else serverB
    oppserver = serverB if pl == playerA else serverA
    record = recordA if pl == playerA else recordB
    opprecord = recordB if pl == playerA else recordA
    msg.data = "Current State: "
    server.publish(msg)
    for key in recordA:
        msg.data = f"{key}: {recordA[key]}"
        server.publish(msg)
    msg.data = "\n"
    server.publish(msg)
    for key in recordB:
        msg.data = f"{key}: {recordB[key]}"
        server.publish(msg)
    msg.data = "\n"
    server.publish(msg)
    msg.data = f"Round {i}"
    server.publish(msg)
    print(f"Round {i}")
    global curr_mons
    for monster in record.keys():
        msg.data = f"{monster}'s turn: "
        if record[monster]:
            server.publish(msg)
            curr_mons = monster
            rospy.wait_for_message(topic, String, timeout=None)
    msg.data = "\n"
    server.publish(msg)
    if not sum(opprecord.values()):
        server.publish("You win")
        oppserver.publish("You lose")
        rospy.signal_shutdown("G.A.M.E. O.V.E.R.")
        print("G.A.M.E. O.V.E.R.")


if __name__ == '__main__':
    rospy.init_node('server_node', anonymous=True)
    counter = 0
    while not rospy.is_shutdown():
        counter += 1
        body(playerA, counter)
        body(playerB, counter)
