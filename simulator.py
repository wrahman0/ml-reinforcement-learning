import random
import numpy as np
import sys
import itertools
import pprint

usepytwo = False
if sys.version_info[0] < 3:
    usepytwo = True

# these are the probability that a car is behind door 1, 2 or 3
# for the symmetric case discussed in Question 2(b)
# door_probs=[0.3333,0.3333,0.3334]
# for the skewed case in Question 2(c)
door_probs = [0.8, 0.1, 0.1]

# choose an initial door for the car
actual_cd = 1 + list(np.random.multinomial(1, door_probs)).index(1)


## the simulator function.
## inputs (tuple s and integer a)
##      * state s is a tuple giving the previous door picked by the player (pd) and the hosts choice (hc). Each can take on values 0-3, where 0 denotes no choice has been made (start of a game) and 1-3 denote which door has been chosen.
##      * action a is the action by the player - this must be 1,2, or 3 and denotes which door is chosen
## output (tuple with first element being a tuple sp and second being a reward value)
##      * state sp is a tuple (pdp,hcp) giving the updated state after the action a is taken in state (pd,hc)
##      * reward gathered r by taking a in state (pd,hc) and ending up in (pdp,hcp)
def simulator(s, a):
    # use the global car door variable (this is hidden to the player who sees the simulator as a black box)
    global actual_cd
    pd = s[0]
    hc = s[1]

    # new value of picked door based on action
    if pd == 0:
        pdp = a
    else:  # resets every second round
        pdp = 0

    # choose a door for the host - based on the actual car door in this game
    if hc == 0:
        # the possible choices are a door in 1,2 or 3
        rem_cardoors = [1, 2, 3]
        # with the actual car door removed,
        rem_cardoors.remove(actual_cd)
        # and the choice of the player removed.
        if a in rem_cardoors:
            rem_cardoors.remove(a)
        # a random choice in the remaining set (which may be a single door)
        hcp = rem_cardoors[random.randint(0, len(rem_cardoors) - 1)]
    else:  # resets every second round
        hcp = 0

    # reward gathered after the final choice (when hc is non-zero)
    if hc == 0 or not a == actual_cd:
        r = 0
    else:
        r = 1

    # reset actual car door in the second round in preparation for the next game
    if not hc == 0:
        actual_cd = 1 + list(np.random.multinomial(1, door_probs)).index(1)
    # return new state and reward
    return (pdp, hcp), r


def get_error(r, y, Q, s, a, sp):
    # get the max
    mx = max(Q[str((sp, 1))], max(Q[str((sp, 2))], Q[str((sp, 1))]))
    return abs((r + y * mx) - Q[str((s, a))])


def update_q_table(s, a, sp, Q, r):
    alpha = .1
    y = 0.75
    key = str((s, a))
    mx = max(Q[str((sp, 1))], max(Q[str((sp, 2))], Q[str((sp, 3))]))
    Q[key] = Q[key] + alpha * (r + y*mx - Q[key])


def get_best_action(s, Q):
    number = random.randint(1, 100)
    if number < 10:
        return random.randint(1, 3)
    else:
        rewards = [Q[str((s, 1))], Q[str((s, 2))], Q[str((s, 3))]]
        max_num = max(rewards)
        max_idx = []
        for i in [0, 1, 2]:
            if max_num == rewards[i]:
                max_idx.append(i + 1)
        return max_idx[random.randint(0, len(max_idx)-1)]


## a simple test program to show how this works
if __name__ == "__main__":
    # default initial state- must be (0,0)
    Q = {}
    pp = pprint.PrettyPrinter(2)
    possible_inputs = itertools.product(itertools.product([0, 1, 2, 3], [0, 1, 2, 3]), [1, 2, 3])
    for i in possible_inputs:
        Q[str(i)] = 0.0

    sumr = 0
    r = 0
    y = 0.75
    s = (0, 0)
    sp = 0

    has_converged = False
    while not has_converged:
        sum_err = 0
        for step in range(0, 1000):
            a = get_best_action(s, Q)
            (sp, r) = simulator(s, a)
            update_q_table(s, a, sp, Q, r)
            sum_err += get_error(r, y, Q, s, a, sp)
            s = sp
        has_converged = (sum_err / 1000) < 0.1

    print "pd\thc\t1\t\t2\t\t3"
    for t_s in itertools.product([0, 1, 2, 3], [0, 1, 2, 3]):
        print "%s\t%s\t%.2f\t%.2f\t%.2f" % (t_s[0], t_s[1], Q[str(((t_s[0], t_s[1]), 1))], Q[str(((t_s[0], t_s[1]), 2))], Q[str(((t_s[0], t_s[1]), 3))])