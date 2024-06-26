/*
 * Copyright (c) 2003-2005 The Regents of The University of Michigan
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Authors: Erik Hallnor
 */

/**
 * @file
 * Declaration of a fully associative LRU tag store.
 */

#ifndef __MEM_CACHE_TAGS_FA_LRU_HH__
#define __MEM_CACHE_TAGS_FA_LRU_HH__

#include <list>

#include "base/hashmap.hh"
#include "mem/cache/tags/base.hh"
#include "mem/cache/blk.hh"
#include "mem/packet.hh"

/**
 * A fully associative cache block.
 */
class FALRUBlk : public CacheBlk
{
public:
    /** The previous block in LRU order. */
    FALRUBlk *prev;
    /** The next block in LRU order. */
    FALRUBlk *next;
    /** Has this block been touched? */
    bool isTouched;

    /**
     * A bit mask of the sizes of cache that this block is resident in.
     * Each bit represents a power of 2 in MB size cache.
     * If bit 0 is set, this block is in a 1MB cache
     * If bit 2 is set, this block is in a 4MB cache, etc.
     * There is one bit for each cache smaller than the full size (default
     * 16MB).
     */
    int inCache;
};

/**
 * A fully associative LRU cache. Keeps statistics for accesses to a number of
 * cache sizes at once.
 */
class FALRU : public BaseTags
{
  public:
    /** Typedef the block type used in this class. */
    typedef FALRUBlk BlkType;
    /** Typedef a list of pointers to the local block type. */
    typedef std::list<FALRUBlk*> BlkList;

  protected:
    /** The block size of the cache. */
    const unsigned blkSize;
    /** The size of the cache. */
    const unsigned size;
    /** The hit latency of the cache. */
    const unsigned hitLatency;

    /** Array of pointers to blocks at the cache size  boundaries. */
    FALRUBlk **cacheBoundaries;
    /** A mask for the FALRUBlk::inCache bits. */
    int cacheMask;
    /** The number of different size caches being tracked. */
    unsigned numCaches;

    /** The cache blocks. */
    FALRUBlk *blks;

    /** The MRU block. */
    FALRUBlk *head;
    /** The LRU block. */
    FALRUBlk *tail;

    /** Hash table type mapping addresses to cache block pointers. */
    typedef m5::hash_map<Addr, FALRUBlk *, m5::hash<Addr> > hash_t;
    /** Iterator into the address hash table. */
    typedef hash_t::const_iterator tagIterator;

    /** The address hash table. */
    hash_t tagHash;

    /**
     * Find the cache block for the given address.
     * @param addr The address to find.
     * @return The cache block of the address, if any.
     */
    FALRUBlk * hashLookup(Addr addr) const;

    /**
     * Move a cache block to the MRU position.
     * @param blk The block to promote.
     */
    void moveToHead(FALRUBlk *blk);

    /**
     * Check to make sure all the cache boundaries are still where they should
     * be. Used for debugging.
     * @return True if everything is correct.
     */
    bool check();

    /**
     * @defgroup FALRUStats Fully Associative LRU specific statistics
     * The FA lru stack lets us track multiple cache sizes at once. These
     * statistics track the hits and misses for different cache sizes.
     * @{
     */

    /** Hits in each cache size >= 128K. */
    Stats::Vector hits;
    /** Misses in each cache size >= 128K. */
    Stats::Vector misses;
    /** Total number of accesses. */
    Stats::Scalar accesses;

    /**
     * @}
     */

public:
    /**
     * Construct and initialize this cache tagstore.
     * @param blkSize The block size of the cache.
     * @param size The size of the cache.
     * @param hit_latency The hit latency of the cache.
     */
    FALRU(unsigned blkSize, unsigned size, unsigned hit_latency);
    ~FALRU();

    /**
     * Register the stats for this object.
     * @param name The name to prepend to the stats name.
     */
    void regStats(const std::string &name);

    /**
     * Invalidate a cache block.
     * @param blk The block to invalidate.
     */
    void invalidateBlk(BlkType *blk);
    void invalidateBlk(BlkType *blk, uint64_t tid){
        invalidateBlk(blk);
    }

    /**
     * Access block and update replacement data.  May not succeed, in which case
     * NULL pointer is returned.  This has all the implications of a cache
     * access and should only be used as such.
     * Returns the access latency and inCache flags as a side effect.
     * @param addr The address to look for.
     * @param asid The address space ID.
     * @param lat The latency of the access.
     * @param inCache The FALRUBlk::inCache flags.
     * @return Pointer to the cache block.
     */
    FALRUBlk* accessBlock(Addr addr, int &lat, int context_src);
    FALRUBlk* accessBlock(Addr addr, int &lat, int context_src, uint64_t tid){
        return accessBlock(addr, lat, context_src);
    }

    /**
     * Find the block in the cache, do not update the replacement data.
     * @param addr The address to look for.
     * @param asid The address space ID.
     * @return Pointer to the cache block.
     */
    FALRUBlk* findBlock(Addr addr) const;
    FALRUBlk* findBlock(Addr addr, uint64_t tid) const{
        return findBlock( addr, tid );
    }

    /**
     * Find a replacement block for the address provided.
     * @param pkt The request to a find a replacement candidate for.
     * @param writebacks List for any writebacks to be performed.
     * @return The block to place the replacement in.
     */
    FALRUBlk* findVictim(Addr addr, PacketList & writebacks);
    FALRUBlk* findVictim(Addr addr, PacketList & writebacks,
            uint64_t tid){
        return findVictim( addr, writebacks );
    }

    void insertBlock(Addr addr, BlkType *blk, int context_src);
    void insertBlock(Addr addr, BlkType *blk, int context_src, uint64_t tid){
        insertBlock( addr, blk, context_src );
    }

    /**
     * Return the hit latency of this cache.
     * @return The hit latency.
     */
    int getHitLatency() const
    {
        return hitLatency;
    }

    /**
     * Return the block size of this cache.
     * @return The block size.
     */
    unsigned
    getBlockSize() const
    {
        return blkSize;
    }

    /**
     * Return the subblock size of this cache, always the block size.
     * @return The block size.
     */
    unsigned
    getSubBlockSize() const
    {
        return blkSize;
    }

    /**
     * Align an address to the block size.
     * @param addr the address to align.
     * @return The aligned address.
     */
    Addr blkAlign(Addr addr) const
    {
        return (addr & ~(Addr)(blkSize-1));
    }

    /**
     * Generate the tag from the addres. For fully associative this is just the
     * block address.
     * @param addr The address to get the tag from.
     * @return The tag.
     */
    Addr extractTag(Addr addr) const
    {
        return blkAlign(addr);
    }

    /**
     * Return the set of an address. Only one set in a fully associative cache.
     * @param addr The address to get the set from.
     * @return 0.
     */
    int extractSet(Addr addr) const
    {
        return 0;
    }

    /**
     * Calculate the block offset of an address.
     * @param addr the address to get the offset of.
     * @return the block offset.
     */
    int extractBlkOffset(Addr addr) const
    {
        return (addr & (Addr)(blkSize-1));
    }

    /**
     * Regenerate the block address from the tag and the set.
     * @param tag The tag of the block.
     * @param set The set the block belongs to.
     * @return the block address.
     */
    Addr regenerateBlkAddr(Addr tag, int set) const
    {
        return (tag);
    }

    /**
     *iterated through all blocks and clear all locks
     *Needed to clear all lock tracking at once
     */
    virtual void clearLocks();
};

#endif // __MEM_CACHE_TAGS_FA_LRU_HH__
