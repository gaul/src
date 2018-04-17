/**
 * Demonstrate Java and Guava Collection overheads.
 *
 * Run with:
 * export CLASSPATH=.:$HOME/.m2/repository/com/google/guava/guava/19.0/guava-19.0.jar; javac CollectionOverhead.java && for i in ArrayDeque ArrayList Cache ConcurrentHashMap ConcurrentHashMultiset ConcurrentLinkedDeque ConcurrentSkipListMap ConcurrentSkipListSet EnumMap EnumSet HashMap HashMultiset HashSet ImmutableList ImmutableMap ImmutableMultiset ImmutableRangeMap ImmutableSet ImmutableSortedMap ImmutableSortedSet LinkedHashMap LinkedHashMultiset LinkedHashSet LinkedList MapMaker PriorityQueue TreeMap TreeMultiset TreeRangeMap TreeSet; do java CollectionOverhead $i $((8 * 1024 * 1024)) 1 || break; done
 *
 * ArrayDeque                8
 * ArrayList                 4
 * Cache                    56
 * ConcurrentHashMap        40
 * ConcurrentHashMultiset   56
 * ConcurrentLinkedDeque    24
 * ConcurrentSkipListMap    36
 * ConcurrentSkipListSet    36
 * HashMap                  40
 * HashMultiset             56
 * HashSet                  40
 * ImmutableMap             32
 * ImmutableMultiset        32
 * ImmutableRangeMap        64
 * ImmutableSet             12
 * ImmutableSortedMap        8
 * ImmutableSortedSet        4
 * LinkedHashMap            48
 * LinkedHashMultiset       64
 * LinkedHashSet            48
 * LinkedList               24
 * MapMaker                 40
 * PriorityQueue             4
 * TreeMap                  40
 * TreeMultiset             56
 * TreeRangeMap            120
 * TreeSet                  40
 *
 * Another resource:
 * https://github.com/DimitrisAndreou/memory-measurer/blob/master/ElementCostInDataStructures.txt
 */

import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.IOException;
import java.lang.ref.WeakReference;
import java.util.Collection;
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.PriorityQueue;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.ConcurrentSkipListSet;

import com.google.common.base.Charsets;
import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import com.google.common.collect.ConcurrentHashMultiset;
import com.google.common.collect.HashMultiset;
import com.google.common.collect.ImmutableCollection;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMultiset;
import com.google.common.collect.ImmutableRangeMap;
import com.google.common.collect.ImmutableSet;
import com.google.common.collect.ImmutableSortedMap;
import com.google.common.collect.ImmutableSortedSet;
import com.google.common.collect.LinkedHashMultiset;
import com.google.common.collect.Lists;
import com.google.common.collect.MapMaker;
import com.google.common.collect.Maps;
import com.google.common.collect.Queues;
import com.google.common.collect.Range;
import com.google.common.collect.RangeMap;
import com.google.common.collect.Sets;
import com.google.common.collect.TreeMultiset;
import com.google.common.collect.TreeRangeMap;
import com.google.common.io.CharStreams;

public final class CollectionOverhead {
    public static void main(final String[] args) throws IOException {
        if (args.length != 3) {
            System.out.println("Usage: java CollectionOverhead" +
                    " collection-type collection-size num-collections");
            System.exit(1);
        }
        String collectionType = args[0];
        int collectionSize = Integer.parseInt(args[1], /*radix=*/ 10);
        int numCollections = Integer.parseInt(args[2], /*radix=*/ 10);

        Collection<Object> objects = Lists.newArrayList();
        for (int i = 0; i < numCollections; ++i) {
            objects.add(populateCollection(args[0], collectionSize));
        }

        forceGarbageCollection();

        String output = runCommand(new String[] {
                "sh", "-c", "jmap -histo:live $PPID" +
                " | awk '$4 !~ /java.lang.Integer/ && $1 !~ /Total/{x += $3} END{print x}'"});
        long numBytes = Long.parseLong(output.trim());
        System.out.printf("%-24s%8d%8d\n", args[0],
                (long) numBytes / numCollections,
                (long) (numBytes / (double) collectionSize) / numCollections);

        // prevent GC of map until after jmap
        Object object = objects;
    }

    private static Object populateCollection(String type, int size) {
        Collection<Integer> collection = null;
        Map<Integer, Integer> map = null;
        EnumMap<TestEnum, TestEnum> enumMap = null;
        EnumSet<TestEnum> enumSet = null;
        ImmutableCollection.Builder<Integer> collectionBuilder = null;
        ImmutableMap.Builder<Integer, Integer> mapBuilder = null;
        RangeMap<Integer, Integer> rangeMap = null;
        ImmutableRangeMap.Builder<Integer, Integer> rangeMapBuilder = null;

        if (type.equals("ArrayDeque")) {
            collection = Queues.newArrayDeque();
        } else if (type.equals("ArrayList")) {
            collection = Lists.newArrayListWithCapacity(size);
        } else if (type.equals("Cache")) {
            Cache<Integer, Integer> cache = CacheBuilder.newBuilder().build();
            map = cache.asMap();
        } else if (type.equals("ConcurrentHashMap")) {
            map = new ConcurrentHashMap<>(/*16, 0.75f, 16*/);
        } else if (type.equals("ConcurrentHashMultiset")) {
            collection = ConcurrentHashMultiset.create();
        } else if (type.equals("ConcurrentLinkedDeque")) {
            collection = new ConcurrentLinkedDeque<>();
        } else if (type.equals("ConcurrentSkipListMap")) {
            map = new ConcurrentSkipListMap<>();
        } else if (type.equals("ConcurrentSkipListSet")) {
            collection = new ConcurrentSkipListSet<>();
        } else if (type.equals("EnumMap")) {
            enumMap = new EnumMap<>(TestEnum.class);
        } else if (type.equals("EnumSet")) {
            enumSet = EnumSet.noneOf(TestEnum.class);
        } else if (type.equals("HashMap")) {
            map = Maps.newHashMapWithExpectedSize(size);
        } else if (type.equals("HashMultiset")) {
            collection = HashMultiset.create(size);
        } else if (type.equals("HashSet")) {
            collection = Sets.newHashSetWithExpectedSize(size);
        } else if (type.equals("ImmutableList")) {
            collectionBuilder = ImmutableList.builder();
        } else if (type.equals("ImmutableMap")) {
            mapBuilder = ImmutableMap.builder();
        } else if (type.equals("ImmutableMultiset")) {
            collectionBuilder = ImmutableMultiset.builder();
        } else if (type.equals("ImmutableRangeMap")) {
            rangeMapBuilder = ImmutableRangeMap.builder();
        } else if (type.equals("ImmutableSet")) {
            collectionBuilder = ImmutableSet.builder();
        } else if (type.equals("ImmutableSortedMap")) {
            mapBuilder = ImmutableSortedMap.naturalOrder();
        } else if (type.equals("ImmutableSortedSet")) {
            collectionBuilder = ImmutableSortedSet.naturalOrder();
        } else if (type.equals("LinkedHashMap")) {
            map = Maps.newLinkedHashMapWithExpectedSize(size);
        } else if (type.equals("LinkedHashMultiset")) {
            collection = LinkedHashMultiset.create(size);
        } else if (type.equals("LinkedHashSet")) {
            collection = Sets.newLinkedHashSetWithExpectedSize(size);
        } else if (type.equals("LinkedList")) {
            collection = Lists.newLinkedList();
        } else if (type.equals("MapMaker")) {
            map = new MapMaker().concurrencyLevel(1).makeMap();
        } else if (type.equals("PriorityQueue")) {
            collection = new PriorityQueue<Integer>(size);
        } else if (type.equals("TreeMap")) {
            map = Maps.newTreeMap();
        } else if (type.equals("TreeMultiset")) {
            collection = TreeMultiset.create();
        } else if (type.equals("TreeRangeMap")) {
            rangeMap = TreeRangeMap.create();
        } else if (type.equals("TreeSet")) {
            collection = Sets.newTreeSet();
        } else {
            System.out.println("Could not find Collection implementation.");
            System.exit(1);
        }

        if (collection != null) {
            for (int i = 0; i < size; ++i) {
                collection.add(i);
            }
        } else if (map != null) {
            for (int i = 0; i < size; ++i) {
                Integer ii = i;
                map.put(ii, ii);
            }
        } else if (enumMap != null) {
            TestEnum[] values = TestEnum.values();
            for (int i = 0; i < size && i < values.length; ++i) {
                enumMap.put(values[i], values[i]);
            }
        } else if (enumSet != null) {
            TestEnum[] values = TestEnum.values();
            for (int i = 0; i < size && i < values.length; ++i) {
                enumSet.add(values[i]);
            }
        } else if (mapBuilder != null) {
            for (int i = 0; i < size; ++i) {
                Integer ii = i;
                mapBuilder.put(ii, ii);
            }
            map = mapBuilder.build();
            mapBuilder = null;
        } else if (collectionBuilder != null) {
            for (int i = 0; i < size; ++i) {
                collectionBuilder.add(i);
            }
            collection = collectionBuilder.build();
            collectionBuilder = null;
        } else if (rangeMap != null) {
            for (int i = 0; i < size; ++i) {
                Integer ii = i;
                rangeMap.put(Range.closedOpen(ii, i + 1), ii);
            }
        } else if (rangeMapBuilder != null) {
            for (int i = 0; i < size; ++i) {
                Integer ii = i;
                rangeMapBuilder.put(Range.closedOpen(ii, i + 1), ii);
            }
            rangeMap = rangeMapBuilder.build();
        }

        if (collection != null) {
            return collection;
        } else if (enumMap != null) {
            return enumMap;
        } else if (enumSet != null) {
            return enumSet;
        } else if (map != null) {
            return map;
        } else if (rangeMap != null) {
            return rangeMap;
        } else {
            return null;
        }
    }

    private static void forceGarbageCollection() {
        Object obj = new Object();
        WeakReference<Object> ref = new WeakReference<Object>(obj);
        obj = null;
        while (ref.get() != null) {
            System.gc();
        }
    }

    // TODO: exit code
    private static String runCommand(final String[] args) throws IOException {
        Process child = Runtime.getRuntime().exec(args);
        InputStream is = child.getInputStream();
        try {
            return CharStreams.toString(new InputStreamReader(is,
                    Charsets.UTF_8));
        } finally {
            is.close();
        }
    }

    private enum TestEnum {
        A0, A1, A2, A3,
        B0, B1, B2, B3,
        C0, C1, C2, C3,
        D0, D1, D2, D3;
    }
}
