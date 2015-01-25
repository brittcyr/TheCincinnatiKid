import java.util.Collections;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Random;
/**
 * This constructs the deal that is going to happen.
 */
class DeckDecoder {
    public static void main(String[] args) {
        String team1name = "TheCincinnatiKid";
        String team2name = "q";
        String team3name = "TheHouse";
        team1name = args[0];
        team2name = args[1];
        team3name = args[2];
        int round = Integer.parseInt(args[3]);
        int numHands = Integer.parseInt(args[4]);

        final int randomSeed = getRandomSeed(team1name, team2name, team3name, round);
        final List<Card[]> decks = getDecks(numHands, randomSeed);
        for (int i = 0; i < decks.size(); i++) {
            Card[] deck = decks.get(i);
            System.out.println(Arrays.toString(deck));
        }
    }
    
    public static List<Card[]> getDecks(final int numHands, final int randomSeed) {
        final List<Card[]> decks = new ArrayList<>();
        final Deck deck = new Deck(randomSeed);
        for (int i = 0; i < numHands; ++i) {
            decks.add(deck.drawCards(11));
            deck.shuffle(true);
        }
        return decks;
    }
    
    public static int getRandomSeed(final String team1, final String team2, final String team3, final int round) {
        if (team1.compareTo(team2) <= 0) {
            if (team3.compareTo(team1) <= 0) {
                return (String.valueOf(team3) + team1 + team2 + round + "randomstring").hashCode();
            }
            if (team3.compareTo(team2) <= 0) {
                return (String.valueOf(team1) + team3 + team2 + round + "randomstring").hashCode();
            }
            return (String.valueOf(team1) + team2 + team3 + round + "randomstring").hashCode();
        }
        else {
            if (team3.compareTo(team2) <= 0) {
                return (String.valueOf(team3) + team2 + team1 + round + "randomstring").hashCode();
            }
            if (team3.compareTo(team1) <= 0) {
                return (String.valueOf(team2) + team3 + team1 + round + "randomstring").hashCode();
            }
            return (String.valueOf(team2) + team1 + team3 + round + "randomstring").hashCode();
        }
    }
}

class Deck
{
    public static final List<Card> UNSHUFFLED_CARDS;
    private List<Card> cards;
    private List<Card> used;
    private Random random;
    
    static {
        UNSHUFFLED_CARDS = new ArrayList<Card>();
        for (int i = 1; i < 5; ++i) {
            for (int j = 2; j < 15; ++j) {
                Deck.UNSHUFFLED_CARDS.add(new Card(j, i));
            }
        }
    }
    
    public Deck() {
        this.cards = new ArrayList<Card>();
        this.used = new ArrayList<Card>();
        this.random = new Random();
        this.cards.addAll(Deck.UNSHUFFLED_CARDS);
        this.shuffle(false);
    }
    
    public Deck(final int seed) {
        this.cards = new ArrayList<Card>();
        this.used = new ArrayList<Card>();
        this.random = new Random();
        this.random = new Random(seed);
        this.cards.addAll(Deck.UNSHUFFLED_CARDS);
        this.shuffle(false);
    }
    
    public void shuffle(final boolean recombine) {
        if (recombine) {
            this.recombine();
        }
        Collections.shuffle(this.cards, this.random);
    }
    
    public Card drawCard() {
        final Card card = this.cards.remove(0);
        this.used.add(card);
        return card;
    }
    
    public Card[] drawCards(final int numCards) {
        final Card[] array = new Card[numCards];
        for (int i = 0; i < numCards; ++i) {
            array[i] = this.drawCard();
        }
        return array;
    }
    
    private void recombine() {
        this.cards.addAll(this.used);
        this.used.clear();
    }
}


class Card
{
    private static final List<Character> ranks;
    private static final List<Character> suits;
    private final int rank;
    private final int suit;
    
    static {
        ranks = Arrays.asList('2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A');
        suits = Arrays.asList('s', 'h', 'd', 'c');
    }
    
    public Card(final int rank, final int suit) {
        this.rank = rank;
        this.suit = suit;
    }
    
    public Card(final char rank, final char suit) {
        this.rank = Card.ranks.indexOf(rank) + 2;
        this.suit = Card.suits.indexOf(suit) + 1;
        if (rank == '\u0001' || suit == '\0') {
            throw new IllegalArgumentException("Invalid rank (" + rank + ") or suit + (" + suit + ")");
        }
    }
    
    public Card(final String rs) {
        this.rank = Card.ranks.indexOf(rs.charAt(0)) + 2;
        this.suit = Card.suits.indexOf(rs.charAt(1)) + 1;
        if (this.rank == 1 || this.suit == 0) {
            throw new IllegalArgumentException("Invalid rank (" + this.rank + ") or suit + (" + this.suit + ")");
        }
    }
    
    public int getRank() {
        return this.rank;
    }
    
    public int getSuit() {
        return this.suit;
    }
    
    @Override
    public String toString() {
        return String.valueOf(Card.ranks.get(this.rank - 2).toString()) + Card.suits.get(this.suit - 1).toString();
    }
    
    public String toFilename() {
        final String cardName = this.toString();
        return "images/cards/" + cardName + ".gif";
    }
    
    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = 31 * result + this.rank;
        result = 31 * result + this.suit;
        return result;
    }
    
    @Override
    public boolean equals(final Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null) {
            return false;
        }
        if (this.getClass() != obj.getClass()) {
            return false;
        }
        final Card other = (Card)obj;
        return this.rank == other.rank && this.suit == other.suit;
    }
    
    public static Card[] fromStrings(final String... strings) {
        final Card[] cards = new Card[strings.length];
        for (int i = 0; i < strings.length; ++i) {
            cards[i] = new Card(strings[i]);
        }
        return cards;
    }
}
