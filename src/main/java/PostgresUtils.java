import org.apache.kafka.common.protocol.types.Field;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class PostgresUtils {

    public static Connection connectToPostgres(String url, String user, String password)  {
        Connection conn = null;
        try {
            conn = DriverManager.getConnection(url, user, password);
            System.out.println("Connected to the PostgreSQL server successfully.");
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        return conn;
    }

    public static void createTables(Connection conn, String user){

        try{
            String friends = String.format("CREATE TABLE IF NOT EXISTS " +
                    "%s_friends (user_id INTEGER NOT NULL PRIMARY KEY, screen_name varchar(225) " +
                            "NOT NULL UNIQUE)",user);
            String tweets = String.format("CREATE TABLE IF NOT EXISTS " +
                    "tweets_from_%s_friends (id INTEGER NOT NULL PRIMARY KEY, text varchar(225) " +
                    "NOT NULL," +
                    "user_id INTEGER," +
                    "FOREIGN KEY (user_id) REFERENCES %s_friends (user_id))",user, user);

            System.out.println(friends);
            System.out.println(tweets);
            PreparedStatement ps = conn.prepareStatement(friends);
            ps.executeUpdate();
            ps = conn.prepareStatement(tweets);
            ps.executeUpdate();
            ps.close();
        }catch (SQLException e) {
            System.out.println(e.getMessage());
        }
    }



}
